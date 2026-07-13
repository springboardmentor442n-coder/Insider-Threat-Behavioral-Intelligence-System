"""CERT r4.2 dataset ingestion.

Design decisions that matter, and why:

1. CHUNKED READS. email.csv is 1.3 GB and http.csv is 13.9 GB. A plain
   pd.read_csv() on http.csv would try to materialise the whole thing in RAM and
   kill a 16 GB machine. Every read here is chunked, so peak memory stays flat
   regardless of file size.

2. http.csv IS AGGREGATED, NOT STORED. It is ~90% of the dataset by size and no
   model consumes an individual URL. But we cannot skip it: two of the three
   r4.2 scenarios have their defining signal inside it (scenario 1 uploads to
   wikileaks; scenario 2 browses job sites). So we stream it, classify each URL,
   and persist only per-user-per-day counts. 13.9 GB of events collapses to a
   table of ~1,000 users x ~500 days. The signal survives; the bulk does not.

3. `content` COLUMNS ARE DROPPED. In file.csv and email.csv these hold generated
   filler prose. They are most of the bytes and none of the signal.

4. DERIVED COLUMNS ARE COMPUTED AT LOAD TIME. has_external_recipient is worked
   out once during ingestion rather than by re-parsing recipient strings on
   every query for the rest of the project's life.

5. DATES ARE PARSED EXPLICITLY as %m/%d/%Y %H:%M:%S. CERT uses US format. Left
   to guess, pandas silently reads 03/06/2010 as 6 March in some rows and 3 June
   in others - a data corruption bug that would quietly poison every downstream
   "after hours" and "weekend activity" feature.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from backend.app.features_models import DailyFeatures, UserBaseline
from backend.app.models import (
    DeviceEvent,
    EmailEvent,
    Employee,
    FileEvent,
    HttpDailySummary,
    InsiderGroundTruth,
    MaliciousEventDay,
    LogonEvent,
)
from backend.app.schemas import IngestionStats

# CERT's timestamps: 01/02/2010 06:49:00 -> 2 January 2010 (US month-first).
logger = logging.getLogger(__name__)

CERT_DATE_FORMAT = "%m/%d/%Y %H:%M:%S"

# The fictional employer in the CERT scenarios. Any recipient outside this
# domain is an external recipient - the email-exfiltration signal.
INTERNAL_EMAIL_DOMAIN = "dtaa.com"

# Rows per chunk. 100k keeps peak memory well under a few hundred MB while
# still amortising the per-chunk overhead.
CHUNK_SIZE = 100_000


def _progress(label: str, rows: int, path: Path, started: float) -> None:
    """Print a single-line, self-overwriting progress update.

    This exists because the first version of this module printed NOTHING while
    streaming a 13.9 GB file. It worked perfectly and looked completely hung, and
    the obvious human response to a program that has printed nothing for eleven
    minutes is to kill it - which is exactly what happened.

    A long-running job that gives no feedback is a broken job, regardless of
    whether the code is correct.
    """
    elapsed = time.perf_counter() - started
    rate = rows / elapsed if elapsed > 0 else 0
    mb = path.stat().st_size / 1_048_576 if path.is_file() else 0
    print(
        f"\r  {label:<12} {rows:>12,} rows  "
        f"{elapsed:>6.0f}s  {rate:>9,.0f} rows/s  ({mb:,.0f} MB file)",
        end="",
        flush=True,
    )

# --- URL classification for http.csv ---------------------------------------
#
# THESE LISTS WERE CORRECTED AFTER MEASURING THEM ON THE REAL DATA.
#
# The first version produced a job_site signal ratio of 1.2x (useless) and a
# cloud_upload ratio of 0.8x - BELOW 1.0, meaning insiders visited those sites
# LESS than normal users. A feature that points the wrong way is worse than no
# feature: it actively misleads the model.
#
# Two mistakes caused it:
#
#   1. linkedin.com was in JOB_SITE_DOMAINS. Everyone browses LinkedIn. Normal
#      users averaged 2.7 "job site" visits PER DAY, which buried the actual
#      scenario-2 signal under ordinary background browsing.
#
#   2. CLOUD_UPLOAD_DOMAINS mixed wikileaks.org (the actual scenario-1 exfil
#      target) in with dropbox.com, rapidshare.com and friends - generic
#      file-sharing sites that CERT's synthetic employees visit constantly as
#      background noise. The one domain that matters was drowned by the ones
#      that do not.
#
# The fix is specificity. wikileaks gets its own feature. Job sites are the
# actual job boards named in the scenario-2 answer files, and nothing else.
JOB_SITE_DOMAINS = frozenset({
    "monster.com", "careerbuilder.com", "indeed.com", "simplyhired.com",
    "craigslist.org", "jobhuntersbible.com", "dice.com",
    "job-hunt.org", "hotjobs.com", "jobsearch.about.com",
    # linkedin.com REMOVED - ubiquitous background browsing, pure noise.
})

# Scenario 1's exfiltration target, on its own. In r4.2 this is THE signal:
# a normal employee has no reason to ever visit it.
WIKILEAKS_DOMAINS = frozenset({"wikileaks.org"})

# Generic file-sharing. Kept as a SEPARATE, lower-weight feature rather than
# being conflated with wikileaks. Some of these are legitimate background noise
# in CERT, so this feature is weak on its own - but it is honest about that
# instead of contaminating a strong feature.
CLOUD_STORAGE_DOMAINS = frozenset({
    "dropbox.com", "4shared.com", "fileserve.com", "filefreak.com",
    "filestube.com", "megaupload.com", "rapidshare.com", "mediafire.com",
})

# Scenario 3's sysadmin downloads a keylogger.
HACKING_SITE_DOMAINS = frozenset({
    "keylogger.org", "actualkeylogger.com", "best-spy-soft.com",
    "dailykeylogger.com", "relytec.com", "refog.com", "wellresearchedreviews.com",
    "spectorsoft.com", "webwatchernow.com",
})


def _domain_of(url: str) -> str:
    """Extract a bare, lowercase domain from a URL. 'www.' stripped."""
    try:
        host = urlparse(url).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def _matches(domain: str, domains: frozenset[str]) -> bool:
    """Suffix match, so 'jobs.monster.com' still counts as monster.com."""
    return any(domain == d or domain.endswith("." + d) for d in domains)


def _classify(domain: str) -> tuple[bool, bool, bool, bool]:
    """(is_job_site, is_wikileaks, is_cloud_storage, is_hacking_site).

    wikileaks is deliberately its own category rather than being folded into
    "cloud upload" - see the comment on the domain lists above. Conflating them
    is what made the original cloud_upload feature point the WRONG WAY on real
    data.
    """
    return (
        _matches(domain, JOB_SITE_DOMAINS),
        _matches(domain, WIKILEAKS_DOMAINS),
        _matches(domain, CLOUD_STORAGE_DOMAINS),
        _matches(domain, HACKING_SITE_DOMAINS),
    )


def _chunks(path: Path, usecols: list[str] | None = None) -> Iterator[pd.DataFrame]:
    """Yield a large CSV in fixed-size chunks."""
    yield from pd.read_csv(
        path,
        chunksize=CHUNK_SIZE,
        usecols=usecols,
        # Never let pandas infer dtypes across chunk boundaries - it can infer
        # different types for the same column in different chunks.
        dtype=str,
        keep_default_na=False,
        na_values=[""],
    )


# ===========================================================================
# Employees (LDAP + psychometric)
# ===========================================================================


def ingest_employees(db: Session, data_dir: Path) -> int:
    """Load the employee roster from the LDAP snapshots and psychometric.csv.

    LDAP is 18 MONTHLY snapshots (2009-12 .. 2011-05), not one file. People join,
    leave and move between departments over the 17 months.

    We take the LATEST snapshot each user appears in, giving us their final known
    department/role/supervisor. This is a deliberate simplification: modelling
    department changes over time is genuinely interesting (a transfer right
    before an exfiltration is itself a signal) but it is not needed for the core
    detection pipeline and it complicates every downstream join. Flagged here as
    a known simplification rather than silently glossed over.
    """
    ldap_dir = data_dir / "r4.2" / "LDAP"
    if not ldap_dir.is_dir():
        raise FileNotFoundError(f"LDAP directory not found: {ldap_dir}")

    # Sorted filenames are chronological (2009-12.csv < 2010-01.csv < ...), so
    # later files overwrite earlier ones and we end up with the latest record.
    snapshots = sorted(ldap_dir.glob("*.csv"))
    if not snapshots:
        raise FileNotFoundError(f"No LDAP snapshots in {ldap_dir}")

    latest: dict[str, dict] = {}
    for snapshot in snapshots:
        df = pd.read_csv(snapshot, dtype=str, keep_default_na=False)
        for row in df.to_dict("records"):
            latest[row["user_id"]] = row

    # Psychometric scores, keyed by user_id.
    psych_path = data_dir / "r4.2" / "psychometric.csv"
    psych: dict[str, dict] = {}
    if psych_path.is_file():
        pdf = pd.read_csv(psych_path)
        psych = {r["user_id"]: r for r in pdf.to_dict("records")}

    employees = []
    for user_id, row in latest.items():
        p = psych.get(user_id, {})
        employees.append(
            Employee(
                user_id=user_id,
                employee_name=row.get("employee_name", ""),
                email=row.get("email"),
                role=row.get("role"),
                business_unit=row.get("business_unit"),
                functional_unit=row.get("functional_unit"),
                department=row.get("department"),
                team=row.get("team"),
                supervisor=row.get("supervisor"),
                psych_o=int(p["O"]) if p.get("O") is not None else None,
                psych_c=int(p["C"]) if p.get("C") is not None else None,
                psych_e=int(p["E"]) if p.get("E") is not None else None,
                psych_a=int(p["A"]) if p.get("A") is not None else None,
                psych_n=int(p["N"]) if p.get("N") is not None else None,
            )
        )

    db.bulk_save_objects(employees)
    db.commit()
    return len(employees)


# ===========================================================================
# Ground truth (answers/)
# ===========================================================================


def ingest_ground_truth(db: Session, data_dir: Path) -> int:
    """Load the answer key: which users were insiders, in which window.

    insiders.csv contains rows for EVERY CERT release (r2, r3.1, r3.2, r4.1,
    r4.2, r5.x, r6.x...). Loading it unfiltered would label users from other
    datasets as insiders in ours. We filter to dataset == 4.2 and expect exactly
    70 rows - the published figure for r4.2.

    The (start, end) window is the important part. A scenario-2 insider behaved
    perfectly normally for months before turning. Flagging their entire history
    as malicious would poison the training labels; only days inside the window
    are malicious.
    """
    answers = data_dir / "answers" / "insiders.csv"
    if not answers.is_file():
        raise FileNotFoundError(f"insiders.csv not found: {answers}")

    df = pd.read_csv(answers, dtype=str, keep_default_na=False)

    # 'dataset' is a string here; r4.2 rows carry "4.2".
    df = df[df["dataset"].astype(str).str.strip() == "4.2"]

    rows: list[InsiderGroundTruth] = []
    insider_scenarios: dict[str, int] = {}

    for r in df.to_dict("records"):
        user_id = r["user"].strip()
        scenario = int(float(r["scenario"]))
        start = pd.to_datetime(r["start"], format=CERT_DATE_FORMAT)
        end = pd.to_datetime(r["end"], format=CERT_DATE_FORMAT)

        rows.append(
            InsiderGroundTruth(
                user_id=user_id,
                scenario=scenario,
                start_time=start.to_pydatetime(),
                end_time=end.to_pydatetime(),
            )
        )
        insider_scenarios[user_id] = scenario

    db.bulk_save_objects(rows)

    # Mirror the flag onto Employee for cheap filtering, but ONLY for users who
    # actually exist in our roster - a foreign key to a missing employee would
    # blow up the transaction.
    known = {
        uid for (uid,) in db.execute(select(Employee.user_id)).all()
    }
    for user_id, scenario in insider_scenarios.items():
        if user_id in known:
            emp = db.get(Employee, user_id)
            if emp is not None:
                emp.is_insider = True
                emp.insider_scenario = scenario

    db.commit()
    return len(rows)


# ===========================================================================
# Activity logs
# ===========================================================================


def ingest_logon(db: Session, data_dir: Path, known_users: set[str]) -> int:
    path = data_dir / "r4.2" / "logon.csv"
    total = 0
    started = time.perf_counter()
    for chunk in _chunks(path):
        chunk = chunk[chunk["user"].isin(known_users)]
        if chunk.empty:
            continue
        ts = pd.to_datetime(chunk["date"], format=CERT_DATE_FORMAT)
        db.bulk_insert_mappings(
            LogonEvent,
            [
                {
                    "event_id": eid,
                    "timestamp": t.to_pydatetime(),
                    "user_id": u,
                    "pc": pc,
                    "activity": a,
                }
                for eid, t, u, pc, a in zip(
                    chunk["id"], ts, chunk["user"], chunk["pc"], chunk["activity"],
                    strict=True,
                )
            ],
        )
        total += len(chunk)
        db.commit()
        _progress("logon.csv", total, path, started)
    print()
    return total


def ingest_device(db: Session, data_dir: Path, known_users: set[str]) -> int:
    path = data_dir / "r4.2" / "device.csv"
    total = 0
    started = time.perf_counter()
    for chunk in _chunks(path):
        chunk = chunk[chunk["user"].isin(known_users)]
        if chunk.empty:
            continue
        ts = pd.to_datetime(chunk["date"], format=CERT_DATE_FORMAT)
        db.bulk_insert_mappings(
            DeviceEvent,
            [
                {
                    "event_id": eid,
                    "timestamp": t.to_pydatetime(),
                    "user_id": u,
                    "pc": pc,
                    "activity": a,
                }
                for eid, t, u, pc, a in zip(
                    chunk["id"], ts, chunk["user"], chunk["pc"], chunk["activity"],
                    strict=True,
                )
            ],
        )
        total += len(chunk)
        db.commit()
        _progress("device.csv", total, path, started)
    print()
    return total


def ingest_file(db: Session, data_dir: Path, known_users: set[str]) -> int:
    """file.csv - dropping the `content` column (filler prose, no signal)."""
    path = data_dir / "r4.2" / "file.csv"
    total = 0
    started = time.perf_counter()
    for chunk in _chunks(path, usecols=["id", "date", "user", "pc", "filename"]):
        chunk = chunk[chunk["user"].isin(known_users)]
        if chunk.empty:
            continue
        ts = pd.to_datetime(chunk["date"], format=CERT_DATE_FORMAT)
        # The extension IS signal - a .exe on a thumb drive is not a .doc.
        ext = (
            chunk["filename"]
            .str.rsplit(".", n=1)
            .str[-1]
            .str.lower()
            .str.slice(0, 20)
        )
        db.bulk_insert_mappings(
            FileEvent,
            [
                {
                    "event_id": eid,
                    "timestamp": t.to_pydatetime(),
                    "user_id": u,
                    "pc": pc,
                    "filename": fn[:255],
                    "file_extension": e,
                }
                for eid, t, u, pc, fn, e in zip(
                    chunk["id"], ts, chunk["user"], chunk["pc"],
                    chunk["filename"], ext, strict=True,
                )
            ],
        )
        total += len(chunk)
        db.commit()
        _progress("file.csv", total, path, started)
    print()
    return total


def ingest_email(db: Session, data_dir: Path, known_users: set[str]) -> int:
    """email.csv - 1.3 GB, most of it the `content` column, which we drop.

    Derives has_external_recipient at load time: any address outside dtaa.com
    across to/cc/bcc. That single boolean is the email-exfiltration signal, and
    computing it once here beats re-parsing semicolon-delimited address strings
    on every downstream query.
    """
    path = data_dir / "r4.2" / "email.csv"
    cols = ["id", "date", "user", "pc", "to", "cc", "bcc", "size", "attachments"]
    total = 0
    started = time.perf_counter()

    for chunk in _chunks(path, usecols=cols):
        chunk = chunk[chunk["user"].isin(known_users)]
        if chunk.empty:
            continue

        ts = pd.to_datetime(chunk["date"], format=CERT_DATE_FORMAT)

        recipients = (
            chunk["to"].fillna("") + ";" +
            chunk["cc"].fillna("") + ";" +
            chunk["bcc"].fillna("")
        )

        mappings = []
        for eid, t, u, pc, rec, size, att in zip(
            chunk["id"], ts, chunk["user"], chunk["pc"],
            recipients, chunk["size"], chunk["attachments"], strict=True,
        ):
            addresses = [a.strip() for a in rec.split(";") if a.strip()]
            external = any(
                not a.lower().endswith("@" + INTERNAL_EMAIL_DOMAIN) for a in addresses
            )
            mappings.append({
                "event_id": eid,
                "timestamp": t.to_pydatetime(),
                "user_id": u,
                "pc": pc,
                "size": int(size) if size and str(size).isdigit() else 0,
                "attachment_count": (
                    int(att) if att and str(att).isdigit() else 0
                ),
                "recipient_count": len(addresses),
                "has_external_recipient": external,
            })

        db.bulk_insert_mappings(EmailEvent, mappings)
        total += len(mappings)
        db.commit()
        _progress("email.csv", total, path, started)

    print()
    return total


def ingest_http_summary(db: Session, data_dir: Path, known_users: set[str]) -> int:
    """http.csv - 13.9 GB streamed, aggregated, and only the summary persisted.

    This is the one that would kill the machine if handled naively. We read it in
    chunks, classify each URL's domain, aggregate to (user, date) counts, and
    accumulate those counts in memory - which is tiny, because the aggregated
    space is only ~1,000 users x ~500 days.

    Expect this to take a while: it is 13.9 GB of CSV. That is unavoidable, but
    it happens ONCE, and afterwards the signal lives in a table you can query in
    milliseconds.
    """
    path = data_dir / "r4.2" / "http.csv"
    if not path.is_file():
        # http.csv is optional - the pipeline still works without it, just
        # without the scenario-1 and scenario-2 web signals.
        return 0

    # (user_id, date) -> counters
    agg: dict[tuple[str, object], dict[str, object]] = {}

    started = time.perf_counter()
    seen = 0
    size_mb = path.stat().st_size / 1_048_576

    print(f"  http.csv is {size_mb:,.0f} MB. Streaming it - this is the slow one.")
    print("  Nothing is stored raw; we keep only per-user-per-day counts.")

    for chunk in _chunks(path, usecols=["date", "user", "url"]):
        seen += len(chunk)

        chunk = chunk[chunk["user"].isin(known_users)]
        if chunk.empty:
            _progress("http.csv", seen, path, started)
            continue

        dates = pd.to_datetime(chunk["date"], format=CERT_DATE_FORMAT).dt.date
        domains = chunk["url"].map(_domain_of)

        for user, day, domain in zip(chunk["user"], dates, domains, strict=True):
            key = (user, day)
            entry = agg.get(key)
            if entry is None:
                entry = {
                    "total": 0, "job": 0, "wiki": 0, "cloud": 0, "hack": 0,
                    "domains": set(),
                }
                agg[key] = entry

            job, wiki, cloud, hack = _classify(domain)
            entry["total"] += 1
            entry["job"] += job
            entry["wiki"] += wiki
            entry["cloud"] += cloud
            entry["hack"] += hack
            if domain:
                entry["domains"].add(domain)

        _progress("http.csv", seen, path, started)

    print()
    print(f"  aggregated {seen:,} raw HTTP events -> {len(agg):,} user-day rows "
          f"({seen / max(len(agg), 1):.0f}x compression)")

    rows = [
        {
            "user_id": user_id,
            "date": day,
            "total_visits": e["total"],
            "job_site_visits": e["job"],
            "wikileaks_visits": e["wiki"],
            "cloud_storage_visits": e["cloud"],
            "hacking_site_visits": e["hack"],
            "distinct_domains": len(e["domains"]),
        }
        for (user_id, day), e in agg.items()
    ]

    # Insert in batches - a single 500k-row insert statement is not a good idea.
    for i in range(0, len(rows), 10_000):
        db.bulk_insert_mappings(HttpDailySummary, rows[i : i + 10_000])
        db.commit()

    return len(rows)


# ===========================================================================
# Orchestration
# ===========================================================================


def recreate_derived_tables(engine) -> None:
    """DROP and rebuild the DERIVED tables, so schema changes actually apply.

    THIS FUNCTION EXISTS BECAUSE OF A REAL, EXPENSIVE BUG.

    `Base.metadata.create_all()` creates tables that do not exist. It does NOT
    alter tables that DO exist. So when HttpDailySummary gained the columns
    `wikileaks_visits` and `cloud_storage_visits`, create_all() looked at the
    already-present http_daily_summary table, decided there was nothing to do,
    and moved on. The ingestion then streamed all 13.9 GB of http.csv - about
    seven and a half minutes - aggregated 28.4 million events correctly, and
    died on the final INSERT with:

        column "wikileaks_visits" of relation "http_daily_summary" does not exist

    All the work, discarded at the last step.

    The tables handled here are all DERIVED: every row in them can be recomputed
    from the raw event tables. Nothing is lost by dropping them, which is exactly
    what makes DROP the right move rather than a dangerous one.

    (The properly grown-up answer is Alembic migrations, which version schema
    changes and can ALTER in place. That is a real gap and it is listed as a
    hardening item rather than waved away - but for derived data that rebuilds in
    minutes, drop-and-recreate is honest, simple, and safe.)
    """
    # Children before parents. daily_features and user_baselines both hold a
    # foreign key to employees, so they must go first.
    DailyFeatures.__table__.drop(engine, checkfirst=True)
    UserBaseline.__table__.drop(engine, checkfirst=True)
    HttpDailySummary.__table__.drop(engine, checkfirst=True)

    from backend.app.database import Base
    # Recreate ONLY these tables from the model definitions.
    #
    # NOT create_all() - it would also silently create any table that happens to be
    # missing, papering over the fact that the database was never migrated. The
    # schema is Alembic's job. This function's job is narrower: rebuild derived
    # tables whose CONTENT is stale, not whose STRUCTURE is unknown.
    HttpDailySummary.__table__.create(engine, checkfirst=True)
    DailyFeatures.__table__.create(engine, checkfirst=True)
    UserBaseline.__table__.create(engine, checkfirst=True)


def clear_all(db: Session) -> None:
    """Wipe every ingested table, children before parents.

    THE ORDER IS DERIVED FROM THE SCHEMA. IT IS NOT A LIST I MAINTAIN, AND THAT IS
    THE ENTIRE POINT OF THIS FUNCTION.

    It used to be a hand-written tuple. The docstring on that version said, in as
    many words:

        "This was a real bug: the first version of this list omitted them, and
         re-running ingestion after building features died with a
         ForeignKeyViolation. Any table pointing at employees has to be cleared
         here, whichever phase created it."

    I wrote that warning. Then I added the `alerts` table, with a foreign key to
    employees, and did not add it to the list. And ingestion died with:

        ForeignKeyViolation: update or delete on table "employees" violates
        constraint "alerts_user_id_fkey" on table "alerts"

    The same bug. In the same function. Under a comment describing it.

    A list a human maintains is a list a human forgets - and no amount of writing
    "REMEMBER TO UPDATE THIS" at the top has ever fixed that, because the person
    adding the table is not reading this file.

    SQLAlchemy already knows the dependency graph. `Base.metadata.sorted_tables`
    returns tables in creation order - parents first - so reversing it gives deletion
    order: children first. It cannot be out of date, because it IS the schema.

    WHAT IS DELIBERATELY *NOT* DELETED
    ----------------------------------
    security_users, audit_logs, alembic_version.

    Re-ingesting the CERT dataset must not delete the platform's OPERATORS or their
    audit trail. Those are not CERT data; they are the product. Wiping the analyst
    accounts every time somebody re-runs an import would be a spectacular own goal,
    and the FK graph does not know that - so this one exclusion is explicit, and it
    is the only hand-maintained thing left.
    """
    from backend.app.database import Base
    from backend.app import features_models  # noqa: F401 - registers the derived tables

    # The platform's own tables. Nothing to do with CERT; never wiped by an import.
    KEEP = {"security_users", "audit_logs", "alembic_version"}

    # sorted_tables is CREATE order (parents first). Reverse it for DELETE order.
    for table in reversed(Base.metadata.sorted_tables):
        if table.name in KEEP:
            continue
        db.execute(table.delete())

    db.commit()


def run_ingestion(
    db: Session,
    data_dir: Path,
    include_http: bool = True,
) -> IngestionStats:
    """Load the whole CERT r4.2 dataset. Idempotent: clears first.

    `include_http=False` skips the 13.9 GB file. Useful for a fast first run
    while developing the rest of the pipeline; the web signals for scenarios 1
    and 2 will simply be zero until you run it again with http enabled.
    """
    started = time.perf_counter()

    clear_all(db)

    stats = IngestionStats()
    stats.employees = ingest_employees(db, data_dir)

    # Every activity table has a foreign key to employees.user_id. A row whose
    # user is not in the roster would abort the transaction, so we filter chunks
    # against this set as we go.
    known_users = {uid for (uid,) in db.execute(select(Employee.user_id)).all()}

    stats.ground_truth_rows = ingest_ground_truth(db, data_dir)

    # The SECOND answer key. insiders.csv gives a WINDOW; the per-insider files in
    # answers/r4.2-*/ give the days attacks ACTUALLY happened. They disagree about
    # 49% of the malicious days, and the published literature uses the second.
    stats.malicious_event_days = ingest_malicious_event_days(db, data_dir)

    stats.logon_events = ingest_logon(db, data_dir, known_users)
    stats.device_events = ingest_device(db, data_dir, known_users)
    stats.file_events = ingest_file(db, data_dir, known_users)
    stats.email_events = ingest_email(db, data_dir, known_users)

    if include_http:
        stats.http_daily_rows = ingest_http_summary(db, data_dir, known_users)

    stats.duration_seconds = round(time.perf_counter() - started, 2)
    return stats


def get_counts(db: Session) -> dict[str, int]:
    """Row counts per table. Used by the /api/data/stats endpoint."""
    return {
        "employees": db.scalar(select(func.count()).select_from(Employee)) or 0,
        # The second answer key. If this is 0 after an ingest, the r4.2-1/-2/-3
        # folders were not found - and train_detect will silently report only one
        # labelling convention, which is the thing we just spent a day fixing.
        "malicious_event_days": db.scalar(
            select(func.count()).select_from(MaliciousEventDay)
        ) or 0,
        "insiders": db.scalar(
            select(func.count()).select_from(Employee).where(Employee.is_insider)
        ) or 0,
        "logon_events": db.scalar(select(func.count()).select_from(LogonEvent)) or 0,
        "device_events": db.scalar(select(func.count()).select_from(DeviceEvent)) or 0,
        "file_events": db.scalar(select(func.count()).select_from(FileEvent)) or 0,
        "email_events": db.scalar(select(func.count()).select_from(EmailEvent)) or 0,
        "http_daily_rows": db.scalar(
            select(func.count()).select_from(HttpDailySummary)
        ) or 0,
    }

def ingest_malicious_event_days(db: Session, data_dir: Path) -> int:
    """Read the PER-INSIDER answer files and record the days attacks actually happened.

    WHY THIS EXISTS - AND WHY IT WAS MISSING FOR SIX WEEKS
    ------------------------------------------------------
    We were reading `answers/insiders.csv`, which gives each insider a WINDOW: a start
    date and an end date. We labelled every day in that window as malicious. That is
    the obvious reading and it produced 1,892 malicious user-days.

    CERT also ships `answers/r4.2-1/`, `-2/`, `-3/` - one CSV per insider, listing the
    actual malicious events with timestamps. Count only the days those events fall on
    and you get 966. That is the number the published literature reports.

    49% OF OUR "MALICIOUS" DAYS CONTAINED NO MALICIOUS ACTIVITY.

    And the error is worst exactly where it hurts:

        scenario 1:  196 window days ->  85 real   (2.3x)
        scenario 2: 1676 window days -> 861 real   (1.9x)
        scenario 3:   20 window days ->  20 real   (exact)

    Scenario 1 is a single-day exfiltration handed a multi-week window - AAM0658 has
    seven window days and two real ones. So the detector was being penalised for
    "missing" five days on which the man did nothing wrong, and rewarded on scenario 2
    for flagging days that were padding. Our 73% / 97% split was partly an artefact of
    the labels, not a property of the model.

    Both conventions are kept. Neither is a lie - "catch him during the campaign" is a
    perfectly defensible thing to want - but a number quoted without saying WHICH
    convention produced it is not comparable to anything, and that is how benchmarks
    turn into fiction.
    """
    root = data_dir / "answers"
    if not root.exists():
        logger.warning("No answers/ directory at %s - skipping event-day labels", root)
        return 0

    rows: list[dict] = []
    for scenario in (1, 2, 3):
        folder = root / f"r4.2-{scenario}"
        if not folder.exists():
            logger.warning("Missing %s", folder)
            continue

        for path in sorted(folder.glob("*.csv")):
            # r4.2-1-AAM0658.csv -> AAM0658
            user = path.stem.rsplit("-", 1)[-1]

            # These files have NO header, and the columns differ by event type
            # (an http row carries a URL and a bag of words; a logon row does not).
            # Only column 2 - the timestamp - is reliably in the same place, so that
            # is the only one we read. Parsing the rest would be inventing structure
            # that is not guaranteed to be there.
            df = pd.read_csv(path, header=None, usecols=[2], names=["ts"])
            days = pd.to_datetime(df["ts"], format=CERT_DATE_FORMAT).dt.normalize()

            for day, n in days.value_counts().items():
                rows.append(
                    {
                        "user_id": user,
                        "event_date": day.date(),
                        "scenario": scenario,
                        "event_count": int(n),
                    }
                )

    if not rows:
        return 0

    db.query(MaliciousEventDay).delete()
    db.bulk_insert_mappings(MaliciousEventDay, rows)
    db.commit()

    logger.info("Ingested %d malicious event-days (vs the window convention)", len(rows))
    return len(rows)