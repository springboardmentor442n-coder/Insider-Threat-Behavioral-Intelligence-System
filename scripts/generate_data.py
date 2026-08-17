#!/usr/bin/env python
"""Generate a CERT r4.2 *schema-compatible* synthetic activity corpus.

The real CERT Insider Threat Dataset r4.2 is ~10 GB and licence-gated, so this
script produces raw logs in exactly the same shape (logon / device / file /
email / http + monthly LDAP snapshots + an answers/ key). Everything
downstream — feature engineering, training, the API — is identical whether it
runs on this corpus or on the genuine r4.2 drop.

To use the real dataset instead, point CERT_RAW_DIR at the extracted r4.2
folder and skip this script.

    python scripts/generate_data.py --users 120 --days 150
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config  # noqa: E402

ROLES = [
    "ITAdmin", "Salesman", "Electrical Engineer", "Mechanical Engineer",
    "Production Line Worker", "Director", "Technical Writer", "Software Engineer",
    "Computer Scientist", "Security Analyst", "HR Specialist", "Accountant",
]
DEPARTMENTS = [
    "1 - Engineering", "2 - Sales", "3 - Human Resources", "4 - Research",
    "5 - Information Technology", "6 - Finance", "7 - Operations",
]
TEAMS = [f"Team {i}" for i in range(1, 13)]

BENIGN_DOMAINS = [
    "wikipedia.org", "cnn.com", "espn.com", "weather.com", "nytimes.com",
    "stackoverflow.com", "github.com", "reddit.com", "amazon.com", "yahoo.com",
]
CLOUD_JOB_DOMAINS = ["dropbox.com", "drive.google.com", "monster.com", "linkedin.com"]

FILE_EXTS = [".doc", ".pdf", ".zip", ".jpg", ".txt", ".png"]
SENSITIVE_EXTS = [".doc", ".pdf", ".zip"]

INTERNAL_DOMAIN = "dtaa.com"
EXTERNAL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]

FIRST_NAMES = [
    "Alan", "Beth", "Carl", "Dana", "Evan", "Fiona", "Gary", "Hana", "Ivan",
    "Julia", "Kyle", "Lena", "Marco", "Nina", "Omar", "Petra", "Quinn", "Rosa",
    "Sami", "Tara", "Umar", "Vera", "Wade", "Xena", "Yusuf", "Zara",
]
LAST_NAMES = [
    "Adams", "Barnes", "Chen", "Diaz", "Ellis", "Foster", "Gupta", "Hayes",
    "Ito", "Jensen", "Khan", "Lopez", "Meyer", "Novak", "Owens", "Patel",
    "Quinn", "Reyes", "Singh", "Tanaka", "Ulrich", "Vargas", "Walsh", "Yates",
]

# The three CERT r4.2 insider scenarios.
SCENARIOS = {
    1: "Removable-media exfiltration after hours",
    2: "Job-hunting followed by bulk upload to cloud storage",
    3: "Disgruntled admin — credential misuse and sabotage",
}


class Generator:
    def __init__(self, n_users: int, n_days: int, insider_rate: float, seed: int):
        self.rng = np.random.default_rng(seed)
        self.n_users = n_users
        self.n_days = n_days
        self.users = self._make_user_ids(n_users)
        # Business days only, matching the CERT activity calendar.
        self.days = pd.bdate_range("2010-01-04", periods=n_days)
        self.profiles = self._make_profiles()
        self.insiders = self._pick_insiders(insider_rate)
        self._event_id = 0

    # -- identities -------------------------------------------------------
    def _make_user_ids(self, n: int) -> list[str]:
        seen, out = set(), []
        while len(out) < n:
            uid = "".join(self.rng.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 3))
            uid += f"{self.rng.integers(0, 10000):04d}"
            if uid not in seen:
                seen.add(uid)
                out.append(uid)
        return sorted(out)

    def _make_profiles(self) -> pd.DataFrame:
        n = self.n_users
        rng = self.rng
        names = [
            f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}" for _ in range(n)
        ]
        roles = rng.choice(ROLES, n)
        return pd.DataFrame(
            {
                "user": self.users,
                "name": names,
                "role": roles,
                "department": rng.choice(DEPARTMENTS, n),
                "team": rng.choice(TEAMS, n),
                # Baseline intensity varies per person — this is what the UEBA
                # engine later learns as "normal for this user".
                "logon_rate": rng.uniform(1.0, 2.4, n),
                "offhours_rate": rng.gamma(1.2, 0.35, n),
                "pc_rate": rng.uniform(0.02, 0.35, n),
                "usb_rate": rng.gamma(1.0, 0.35, n) * (rng.random(n) < 0.55),
                "file_rate": rng.gamma(1.4, 1.6, n),
                "email_rate": rng.uniform(4.0, 13.0, n),
                "external_ratio": rng.uniform(0.05, 0.45, n),
                "http_rate": rng.uniform(25.0, 130.0, n),
                "cloud_ratio": rng.uniform(0.005, 0.05, n),
            }
        )

    def _pick_insiders(self, rate: float) -> pd.DataFrame:
        n_insiders = max(4, int(round(self.n_users * rate)))
        chosen = self.rng.choice(self.users, size=n_insiders, replace=False)
        # Spread attack windows evenly across the calendar rather than drawing
        # start dates at random: a chronological train/test split needs
        # malicious activity on *both* sides of the cut to be evaluable.
        anchors = np.linspace(0.12, 0.92, n_insiders)
        rows = []
        for user, anchor in zip(chosen, anchors):
            scenario = int(self.rng.integers(1, 4))
            window = int(self.rng.integers(8, 25))
            jitter = self.rng.integers(-4, 5)
            start_idx = int(np.clip(anchor * self.n_days + jitter, 1, self.n_days - window - 1))
            rows.append(
                {
                    "user": user,
                    "scenario": scenario,
                    "start_idx": start_idx,
                    "end_idx": start_idx + window,
                }
            )
        return pd.DataFrame(rows).sort_values("user").reset_index(drop=True)

    def attack_mask(self) -> np.ndarray:
        """(n_users, n_days) boolean — True on a user's attack days."""
        mask = np.zeros((self.n_users, self.n_days), dtype=bool)
        idx = {u: i for i, u in enumerate(self.users)}
        for r in self.insiders.itertuples():
            mask[idx[r.user], r.start_idx : r.end_idx] = True
        return mask

    def scenario_vector(self) -> np.ndarray:
        """(n_users,) int — scenario number per user, 0 for benign users."""
        vec = np.zeros(self.n_users, dtype=int)
        idx = {u: i for i, u in enumerate(self.users)}
        for r in self.insiders.itertuples():
            vec[idx[r.user]] = r.scenario
        return vec

    # -- helpers ----------------------------------------------------------
    def next_ids(self, n: int) -> list[str]:
        ids = [f"{{{i:012X}-{self.rng.integers(0, 1 << 30):08X}}}"
               for i in range(self._event_id, self._event_id + n)]
        self._event_id += n
        return ids

    def _expand(self, counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Turn a (n_users, n_days) count matrix into flat user/day indices."""
        counts = np.maximum(counts.astype(int), 0)
        flat = counts.ravel()
        positions = np.repeat(np.arange(flat.size), flat)
        return positions // self.n_days, positions % self.n_days

    def _timestamps(self, day_idx: np.ndarray, off_hours: np.ndarray) -> pd.Series:
        """Business-hour timestamps, or evening/early-morning when off_hours."""
        n = day_idx.size
        base = self.days.values[day_idx].astype("datetime64[s]").astype(np.int64)
        work = (
            self.rng.integers(7, 18, n) * 3600
            + self.rng.integers(0, 3600, n)
        )
        late = self.rng.integers(18, 24, n) * 3600 + self.rng.integers(0, 3600, n)
        early = self.rng.integers(0, 7, n) * 3600 + self.rng.integers(0, 3600, n)
        off = np.where(self.rng.random(n) < 0.7, late, early)
        secs = np.where(off_hours, off, work)
        return pd.to_datetime(base + secs, unit="s")

    def _pcs(self, user_idx: np.ndarray) -> np.ndarray:
        return np.array([f"PC-{u:04d}" for u in user_idx])

    def _poisson(self, rate_col: str, multiplier: np.ndarray | float = 1.0) -> np.ndarray:
        rates = self.profiles[rate_col].to_numpy()[:, None] * np.ones((1, self.n_days))
        return self.rng.poisson(np.maximum(rates * multiplier, 0))


def _frame(user_idx, day_idx, ts, gen, malicious, extra: dict) -> pd.DataFrame:
    users = np.array(gen.users)[user_idx]
    df = pd.DataFrame(
        {
            "id": gen.next_ids(len(user_idx)),
            "date": ts,
            "user": users,
            "pc": gen._pcs(user_idx),
            **extra,
        }
    )
    df["_malicious"] = malicious
    return df


def build_logon(gen: Generator, attack: np.ndarray, scen: np.ndarray) -> pd.DataFrame:
    rng = gen.rng
    # Normal logon sessions.
    normal = np.maximum(gen._poisson("logon_rate"), 1)
    off = gen._poisson("offhours_rate")
    # Sabotage (scenario 3) and after-hours exfil (scenario 1) add night logons.
    boost = attack * ((scen[:, None] == 3) * 4 + (scen[:, None] == 1) * 2 + 1)
    off_extra = rng.poisson(np.maximum(boost, 0))

    frames = []
    for counts, is_off, mal in [
        (normal, False, False),
        (off, True, False),
        (off_extra, True, True),
    ]:
        ui, di = gen._expand(counts)
        if ui.size == 0:
            continue
        ts = gen._timestamps(di, np.full(ui.size, is_off))
        logon = _frame(ui, di, ts, gen, mal, {"activity": "Logon"})
        logoff = logon.copy()
        logoff["id"] = gen.next_ids(len(logoff))
        logoff["activity"] = "Logoff"
        logoff["date"] = logoff["date"] + pd.to_timedelta(
            rng.integers(30, 240, len(logoff)), unit="m"
        )
        frames += [logon, logoff]

    df = pd.concat(frames, ignore_index=True)

    # A few users legitimately roam between machines.
    roam = rng.random(len(df)) < 0.06
    df.loc[roam, "pc"] = [f"PC-{i:04d}" for i in rng.integers(0, gen.n_users, roam.sum())]

    # Scenario 3 is IT sabotage: the hallmark is lateral movement, so the
    # malicious sessions fan out across many machines rather than staying on
    # the user's own workstation. Without this, sabotage is nearly invisible
    # to the feature set (it would only nudge off_hours_logons).
    scen_of = dict(zip(gen.users, scen))
    sabotage = df["_malicious"] & df["user"].map(scen_of).eq(3)
    if sabotage.any():
        df.loc[sabotage, "pc"] = [
            f"PC-{i:04d}" for i in rng.integers(0, gen.n_users, int(sabotage.sum()))
        ]
    return df


def build_device(gen: Generator, attack: np.ndarray, scen: np.ndarray) -> pd.DataFrame:
    rng = gen.rng
    normal = gen._poisson("usb_rate")
    # Scenarios 1 and 2 lean heavily on removable media.
    extra = rng.poisson(np.maximum(attack * ((scen[:, None] != 3) * 2.5 + 0.5), 0))
    offhours_extra = rng.poisson(np.maximum(attack * (scen[:, None] == 1) * 2.0, 0))

    frames = []
    for counts, is_off, mal in [
        (normal, False, False),
        (extra, False, True),
        (offhours_extra, True, True),
    ]:
        ui, di = gen._expand(counts)
        if ui.size == 0:
            continue
        ts = gen._timestamps(di, np.full(ui.size, is_off))
        conn = _frame(ui, di, ts, gen, mal, {"activity": "Connect"})
        disc = conn.copy()
        disc["id"] = gen.next_ids(len(disc))
        disc["activity"] = "Disconnect"
        disc["date"] = disc["date"] + pd.to_timedelta(
            rng.integers(2, 90, len(disc)), unit="m"
        )
        frames += [conn, disc]
    return pd.concat(frames, ignore_index=True)


def build_file(gen: Generator, attack: np.ndarray, scen: np.ndarray) -> pd.DataFrame:
    rng = gen.rng
    normal = gen._poisson("file_rate")
    # Bulk copy-out during the attack window.
    extra = rng.poisson(np.maximum(attack * ((scen[:, None] != 3) * 14 + 3), 0))

    frames = []
    for counts, mal in [(normal, False), (extra, True)]:
        ui, di = gen._expand(counts)
        if ui.size == 0:
            continue
        # Insiders take a much higher share of sensitive document types.
        p_sensitive = 0.9 if mal else 0.45
        exts = np.where(
            rng.random(ui.size) < p_sensitive,
            rng.choice(SENSITIVE_EXTS, ui.size),
            rng.choice([e for e in FILE_EXTS if e not in SENSITIVE_EXTS], ui.size),
        )
        names = [f"{rng.integers(0, 1 << 24):06X}{e}" for e in exts]
        ts = gen._timestamps(di, np.full(ui.size, mal and rng.random() < 0.5))
        frames.append(
            _frame(ui, di, ts, gen, mal, {"filename": names, "content": "D0-CF-11-E0"})
        )
    return pd.concat(frames, ignore_index=True)


def build_email(gen: Generator, attack: np.ndarray, scen: np.ndarray) -> pd.DataFrame:
    rng = gen.rng
    normal = gen._poisson("email_rate")
    # Scenario 2 mails material to a personal account.
    extra = rng.poisson(np.maximum(attack * ((scen[:, None] == 2) * 8 + 2), 0))

    frames = []
    for counts, mal in [(normal, False), (extra, True)]:
        ui, di = gen._expand(counts)
        if ui.size == 0:
            continue
        users = np.array(gen.users)[ui]
        ext_ratio = gen.profiles["external_ratio"].to_numpy()[ui]
        is_external = rng.random(ui.size) < np.where(mal, 0.95, ext_ratio)
        to = np.where(
            is_external,
            [f"{rng.integers(0, 1 << 20):05X}@{d}" for d in rng.choice(EXTERNAL_DOMAINS, ui.size)],
            [f"{u.lower()}@{INTERNAL_DOMAIN}" for u in np.array(gen.users)[rng.integers(0, gen.n_users, ui.size)]],
        )
        n_attach = np.where(mal, rng.integers(1, 8, ui.size), rng.poisson(0.9, ui.size))
        size = (rng.integers(8_000, 60_000, ui.size) + n_attach * rng.integers(40_000, 400_000, ui.size))
        ts = gen._timestamps(di, np.zeros(ui.size, dtype=bool))
        frames.append(
            _frame(ui, di, ts, gen, mal, {
                "to": to,
                "cc": "",
                "bcc": "",
                "from": [f"{u.lower()}@{INTERNAL_DOMAIN}" for u in users],
                "size": size,
                "attachment_count": n_attach,
                "content": "meeting notes attached",
            })
        )
    return pd.concat(frames, ignore_index=True)


def build_http(gen: Generator, attack: np.ndarray, scen: np.ndarray) -> pd.DataFrame:
    rng = gen.rng
    normal = gen._poisson("http_rate")
    # Job hunting (scenario 2) and cloud uploads spike these domains.
    extra = rng.poisson(np.maximum(attack * ((scen[:, None] == 2) * 18 + 5), 0))

    frames = []
    for counts, mal in [(normal, False), (extra, True)]:
        ui, di = gen._expand(counts)
        if ui.size == 0:
            continue
        cloud_ratio = gen.profiles["cloud_ratio"].to_numpy()[ui]
        is_cloud = rng.random(ui.size) < np.where(mal, 0.8, cloud_ratio)
        domains = np.where(
            is_cloud,
            rng.choice(CLOUD_JOB_DOMAINS, ui.size),
            rng.choice(BENIGN_DOMAINS, ui.size),
        )
        urls = [f"http://www.{d}/{rng.integers(0, 1 << 22):06X}" for d in domains]
        ts = gen._timestamps(di, np.full(ui.size, False))
        frames.append(_frame(ui, di, ts, gen, mal, {"url": urls, "content": "page text"}))
    return pd.concat(frames, ignore_index=True)


def write_ldap(gen: Generator, out_dir: Path):
    ldap_dir = out_dir / "LDAP"
    # Wipe first: a previous run with a different date range leaves month files
    # behind, and the ingestion pipeline globs whatever it finds.
    if ldap_dir.exists():
        shutil.rmtree(ldap_dir)
    ldap_dir.mkdir(parents=True, exist_ok=True)
    months = sorted({d.strftime("%Y-%m") for d in gen.days})
    prof = gen.profiles
    # Supervisors are drawn from the Director/ITAdmin population.
    pool = prof[prof["role"].isin(["Director", "ITAdmin"])]["name"].tolist()
    if not pool:
        pool = prof["name"].tolist()[:5]
    supervisors = gen.rng.choice(pool, len(prof))
    for month in months:
        pd.DataFrame(
            {
                "employee_name": prof["name"],
                "user_id": prof["user"],
                "email": [f"{u.lower()}@{INTERNAL_DOMAIN}" for u in prof["user"]],
                "role": prof["role"],
                "business_unit": "1",
                "functional_unit": "1",
                "department": prof["department"],
                "team": prof["team"],
                "supervisor": supervisors,
            }
        ).to_csv(ldap_dir / f"{month}.csv", index=False)
    return len(months)


def write_answers(gen: Generator, sources: dict[str, pd.DataFrame], out_dir: Path):
    """Write the malicious-event key in CERT answers/ format."""
    answers = out_dir / "answers"
    # Same idempotency concern as LDAP, but far more damaging: a stale answer
    # file silently labels a benign user as an insider in every later run.
    if answers.exists():
        shutil.rmtree(answers)
    answers.mkdir(parents=True, exist_ok=True)
    scen_of = dict(zip(gen.insiders["user"], gen.insiders["scenario"]))

    lines_by_user: dict[str, list[str]] = {}
    for source, df in sources.items():
        mal = df[df["_malicious"]]
        if mal.empty:
            continue
        cols = [c for c in df.columns if c != "_malicious"]
        for row in mal[cols].itertuples(index=False):
            values = [str(v).replace(",", " ") for v in row]
            user = values[2]
            lines_by_user.setdefault(user, []).append(
                f"{source}," + ",".join(values)
            )

    for user, lines in lines_by_user.items():
        folder = answers / f"r4.2-{scen_of.get(user, 1)}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{user}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    ins = gen.insiders.copy()
    ins["dataset"] = "4.2"
    ins["start"] = [gen.days[i].strftime("%m/%d/%Y %H:%M:%S") for i in ins["start_idx"]]
    ins["end"] = [gen.days[i].strftime("%m/%d/%Y %H:%M:%S") for i in ins["end_idx"]]
    ins["details"] = ins["scenario"].map(SCENARIOS)
    ins[["dataset", "scenario", "user", "start", "end", "details"]].to_csv(
        answers / "insiders.csv", index=False
    )
    return len(lines_by_user)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--users", type=int, default=160)
    ap.add_argument("--days", type=int, default=160, help="number of business days")
    ap.add_argument("--insider-rate", type=float, default=0.07)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None, help="output dir (default data/raw)")
    args = ap.parse_args()

    Config.ensure_dirs()
    out_dir = Path(args.out) if args.out else Config.RAW_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating synthetic CERT r4.2 corpus -> {out_dir}")
    gen = Generator(args.users, args.days, args.insider_rate, args.seed)
    attack, scen = gen.attack_mask(), gen.scenario_vector()
    print(f"  {args.users} users | {args.days} business days "
          f"| {len(gen.insiders)} insiders across {gen.insiders['scenario'].nunique()} scenarios")

    sources = {
        "logon": build_logon(gen, attack, scen),
        "device": build_device(gen, attack, scen),
        "file": build_file(gen, attack, scen),
        "email": build_email(gen, attack, scen),
        "http": build_http(gen, attack, scen),
    }

    for name, df in sources.items():
        df = df.sort_values("date").reset_index(drop=True)
        sources[name] = df
        out = df.drop(columns=["_malicious"])
        out.to_csv(out_dir / f"{name}.csv", index=False)
        print(f"  {name}.csv: {len(out):,} events "
              f"({int(df['_malicious'].sum()):,} malicious)")

    n_months = write_ldap(gen, out_dir)
    print(f"  LDAP/: {n_months} monthly snapshots")
    n_files = write_answers(gen, sources, out_dir)
    print(f"  answers/: key written for {n_files} insiders")

    gen.profiles[["user", "name", "role", "department", "team"]].to_csv(
        out_dir / "employee_directory.csv", index=False
    )
    print("Done.")


if __name__ == "__main__":
    main()
