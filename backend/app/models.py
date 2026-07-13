"""Database models.

Two distinct groups of tables live here, and confusing them is the single
easiest way to misunderstand this system:

  PLATFORM tables   - the humans who USE the tool.
                      SecurityUser = an analyst who logs into the dashboard.

  MONITORED tables  - the humans the tool WATCHES.
                      Employee = one of the 1,000 CERT employees under
                      surveillance. They do not log in. They have no password.
                      They are the subject, not the operator.

A Security Analyst (SecurityUser) investigates an Employee. An Employee never
touches this system. Keeping these separate is not pedantry - conflating them
would be a genuine security design flaw.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    text,
    Float,
    JSON,
    UniqueConstraint,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


# ===========================================================================
# PLATFORM: the people who operate the tool
# ===========================================================================


class UserRole(str, enum.Enum):
    """The four roles from the project specification.

    Inheriting from `str` as well as Enum means these serialise straight to
    JSON as "security_analyst" rather than "UserRole.SECURITY_ANALYST".
    """

    SECURITY_ANALYST = "security_analyst"
    SOC_ENGINEER = "soc_engineer"
    SECURITY_MANAGER = "security_manager"
    ADMINISTRATOR = "administrator"


class SecurityUser(Base):
    """An operator of the platform: analyst, SOC engineer, manager, or admin."""

    __tablename__ = "security_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))

    # The bcrypt hash - NEVER the password itself. If this table leaked, an
    # attacker still could not log in as anyone: bcrypt is one-way and salted.
    hashed_password: Mapped[str] = mapped_column(String(255))

    # role carries BOTH a Python default and a SERVER default, and it needs both.
    #
    # The old test had `security_users.role` on a hand-maintained allowlist of
    # columns that were "legitimately" NOT NULL with no default - so nobody ever
    # checked WHY it was there, and the missing server_default sat undetected. The
    # rule-based test found it in one run. A list a human maintains is a list a human
    # forgets; a rule cannot be forgotten.
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.SECURITY_ANALYST,  # least privilege by default
        server_default=UserRole.SECURITY_ANALYST.name,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # --- Brute-force protection -------------------------------------------
    #
    # Without these, /login is an unlimited password-guessing oracle. An attacker
    # with a wordlist and a weekend gets in, and nothing in the logs looks unusual
    # because every individual request is a perfectly ordinary failed login.
    #
    # This is an INSIDER THREAT product. An attacker who compromises a Security
    # Manager account can see every employee's behavioural profile, read the
    # ground-truth insider labels, and - most usefully - find out whether they
    # themselves are being watched. The account is worth attacking.
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Password rotation. A password changed after a token was issued must not leave
    # that token valid - see `password_changed_at` in the JWT validation path.
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class AuditLog(Base):
    """Every consequential action an operator takes.

    This is a security product. "Who looked at whose data, and when" must be
    answerable - both because analysts have access to sensitive behavioural
    data on real people, and because an insider-threat tool is itself a
    tempting target for an insider. The watchers get watched.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    security_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("security_users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), index=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


# ===========================================================================
# MONITORED: the people the tool watches (from the CERT dataset)
# ===========================================================================


class Employee(Base):
    """One of the 1,000 CERT employees. Sourced from the LDAP snapshots.

    `department`, `team` and `role` are what make peer-group comparison
    possible: a 02:00 logon is unremarkable for on-call engineering and
    alarming for HR. Without this table there is no "U" and no "E" in UEBA -
    only per-user anomaly detection, which is a strictly weaker thing.

    `supervisor` matters specifically for CERT scenario 3, where a disgruntled
    sysadmin logs in AS his supervisor. Without the reporting line, that attack
    is invisible.
    """

    __tablename__ = "employees"

    user_id: Mapped[str] = mapped_column(String(20), primary_key=True)  # e.g. AAF0535
    employee_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    business_unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    functional_unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(
        String(100), index=True, nullable=True
    )
    team: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    supervisor: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Big Five personality scores from psychometric.csv.
    # Present in the dataset; we store them but treat them with caution - see
    # the ingestion module for why we do not feed them to the models by default.
    psych_o: Mapped[int | None] = mapped_column(Integer, nullable=True)
    psych_c: Mapped[int | None] = mapped_column(Integer, nullable=True)
    psych_e: Mapped[int | None] = mapped_column(Integer, nullable=True)
    psych_a: Mapped[int | None] = mapped_column(Integer, nullable=True)
    psych_n: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Ground truth from the answers/ folder. NEVER a model input - this is the
    # exam answer key. Using it as a feature would be target leakage and the
    # resulting 99% accuracy would be a lie.
    is_insider: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)
    insider_scenario: Mapped[int | None] = mapped_column(Integer, nullable=True)

    logon_events: Mapped[list[LogonEvent]] = relationship(back_populates="employee")


class LogonEvent(Base):
    """A logon or logoff. From logon.csv."""

    __tablename__ = "logon_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(50))  # CERT's {XXXX-...} id
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("employees.user_id"), index=True
    )
    pc: Mapped[str] = mapped_column(String(20), index=True)
    activity: Mapped[str] = mapped_column(String(20))  # Logon | Logoff

    employee: Mapped[Employee] = relationship(back_populates="logon_events")

    # EVERY behavioural query is "this user, this date range". A composite index
    # on (user_id, timestamp) turns those from a full table scan into an index
    # seek. With ~800k logon rows that is the difference between a dashboard
    # that responds and one that times out.
    __table_args__ = (Index("ix_logon_user_time", "user_id", "timestamp"),)


class DeviceEvent(Base):
    """A USB / removable-media connect or disconnect. From device.csv.

    Central to all three r4.2 scenarios - every one of them involves a thumb
    drive. This is the highest-signal table in the dataset.
    """

    __tablename__ = "device_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("employees.user_id"), index=True
    )
    pc: Mapped[str] = mapped_column(String(20), index=True)
    activity: Mapped[str] = mapped_column(String(20))  # Connect | Disconnect

    __table_args__ = (Index("ix_device_user_time", "user_id", "timestamp"),)


class FileEvent(Base):
    """A file touched on removable media. From file.csv.

    We deliberately DROP the `content` column at ingestion. It is filler text
    (plus a magic-number prefix) that inflates the table enormously and carries
    no detection signal. The filename extension does carry signal.
    """

    __tablename__ = "file_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("employees.user_id"), index=True
    )
    pc: Mapped[str] = mapped_column(String(20), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_extension: Mapped[str | None] = mapped_column(
        String(20), index=True, nullable=True
    )

    __table_args__ = (Index("ix_file_user_time", "user_id", "timestamp"),)


class EmailEvent(Base):
    """An email. From email.csv.

    Derived-at-ingestion columns do the heavy lifting here:
      has_external_recipient - any recipient outside dtaa.com (the fictional
                               employer). This is the data-exfiltration-by-email
                               signal, and computing it once at load time beats
                               re-parsing recipient strings on every query.
      recipient_count        - fan-out; a mass email is scenario 3's payload.

    The `content` column is dropped for the same reason as file.csv: it is
    generated filler, and it is the bulk of the 1.3 GB.
    """

    __tablename__ = "email_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("employees.user_id"), index=True
    )
    pc: Mapped[str] = mapped_column(String(20), index=True)
    size: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    attachment_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    recipient_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    has_external_recipient: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", index=True
    )

    __table_args__ = (Index("ix_email_user_time", "user_id", "timestamp"),)


class HttpDailySummary(Base):
    """Per-user, per-day web activity. Aggregated from http.csv at ingest.

    http.csv is 13.9 GB - roughly 90% of the dataset by size. Storing it raw
    would dwarf everything else and buy us nothing: no model consumes
    individual URLs.

    But we cannot skip it either. Two of the three r4.2 scenarios have their
    defining signal in here:
      scenario 1 -> uploads to wikileaks.org
      scenario 2 -> job-hunting on monster.com / craigslist.org

    So we stream the file in chunks, classify each URL, and keep only the daily
    counts. 13.9 GB of raw events becomes a table of roughly 1,000 users x ~500
    days. The signal survives; the bulk does not.
    """

    __tablename__ = "http_daily_summary"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("employees.user_id"), index=True
    )
    date: Mapped[Date] = mapped_column(Date, index=True)

    total_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Scenario 2: job hunting. linkedin.com is deliberately NOT counted here -
    # everyone browses it, and including it buried the real signal under noise
    # (measured 1.2x lift, i.e. useless). These are the actual job boards.
    job_site_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Scenario 1: the exfiltration target itself, on its own. Originally this was
    # lumped in with generic file-sharing sites, which produced a signal ratio
    # BELOW 1.0 - insiders appeared to visit "cloud upload" sites LESS than
    # normal users, because the noise dominated. Separating it is the fix.
    wikileaks_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Generic file-sharing (dropbox, rapidshare...). Weak on its own - CERT's
    # normal employees browse these routinely - but kept as an honest, separate,
    # low-weight feature rather than contaminating the wikileaks signal.
    cloud_storage_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    hacking_site_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # scenario 3
    distinct_domains: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    __table_args__ = (
        Index("ix_http_user_date", "user_id", "date", unique=True),
    )


class InsiderGroundTruth(Base):
    """The answer key, from answers/. Kept in its own table on purpose.

    Two reasons this is not just a column on Employee:
      1. It records the malicious WINDOW (start..end), not just a flag. A
         scenario-2 insider behaved normally for months before turning. Labelling
         all of their days as malicious would poison the training data.
      2. Keeping it physically separate makes accidental target leakage into a
         feature pipeline much harder. You have to reach for this table
         deliberately.
    """

    __tablename__ = "insider_ground_truth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("employees.user_id"), index=True
    )
    scenario: Mapped[int] = mapped_column(Integer, index=True)  # 1, 2 or 3
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)


class AlertSeverity(str, enum.Enum):
    """The spec's five levels (Module 9).

    The risk score produces FOUR levels. The spec asks for FIVE, and never says what
    "Informational" means. The naive reading - one notch below Low - would mean
    writing an alert row for every low-scoring user-day, which on the real dataset is
    100,467 rows PER RUN. An alert table in which 99.7% of the rows are noise is not
    an alert table; it is a second copy of the feature table with worse ergonomics.

    So Informational earns its place instead:

        CRITICAL       risk >= 50   page someone now
        HIGH           risk >= 40   investigate today
        MEDIUM         risk >= 20   review this week
        LOW            risk >= 10   AND the user already has a MEDIUM+ alert.
                                    A quiet day for someone we are already watching
                                    is worth a row. A quiet day for everyone else
                                    is not.
        INFORMATIONAL  any other day for a user UNDER INVESTIGATION. Context for the
                       investigator, never queued and never paged.

    The table is therefore bounded by (flagged users x their days), not by
    (all users x all days) - and when an analyst opens a case they see the whole
    timeline, quiet days included, which is exactly what an investigation needs.
    """

    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    """The SOC workflow.

    RESOLUTION IS SPLIT INTO TRUE AND FALSE POSITIVE, DELIBERATELY.

    A single "closed" state would throw away the single most valuable piece of data
    this system can generate: the analyst's verdict. Those verdicts are ground truth
    that nobody had to synthesise - they are how you measure precision in production,
    where there IS no answer key, and they are the training signal for the next model.

    A detection system that does not record what its humans decided is a system that
    can never improve, and can never tell you whether it is getting worse.
    """

    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    RESOLVED_TRUE_POSITIVE = "resolved_true_positive"
    RESOLVED_FALSE_POSITIVE = "resolved_false_positive"


class Alert(Base):
    """One alert: one employee, one day, one risk score, one workflow state.

    UNIQUE ON (user_id, alert_date) - AND THAT IS LOAD-BEARING.

    Alert generation is a batch job, and batch jobs get re-run: after a retrain, after
    a bug fix, after someone fat-fingers a date range. Without the constraint, every
    re-run silently duplicates the entire queue, an analyst arrives to find the same
    alert four times, and the only fix is a DELETE against production.

    With it, a re-run UPDATES the score and leaves the analyst's work - their
    assignment, their notes, their verdict - untouched. Re-running the detector must
    never destroy human judgement.
    """

    __tablename__ = "alerts"
    __table_args__ = (
        UniqueConstraint("user_id", "alert_date", name="uq_alert_user_day"),
        Index("ix_alerts_triage", "status", "severity", "alert_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("employees.user_id"), index=True
    )
    alert_date: Mapped[datetime] = mapped_column(Date, index=True)

    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, native_enum=False, length=20), index=True
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, native_enum=False, length=30),
        default=AlertStatus.NEW,
        server_default="NEW",
        index=True,
    )

    # THE SCORES. Both, and they are different things.
    #
    # risk_score is the spec's decomposed 0-100 composite - what an analyst reads and
    # what a tribunal could be shown. ml_probability is the raw model output - a
    # strictly better DETECTOR (measured: +9.8% PR-AUC) and completely opaque.
    #
    # Storing only one would be a mistake. The composite is for humans; the
    # probability is for ranking, for measuring the system, and for retraining. They
    # answer different questions and neither substitutes for the other.
    risk_score: Mapped[float] = mapped_column(Float, index=True)
    ml_probability: Mapped[float] = mapped_column(Float)

    # The five components, and the SHAP top features.
    #
    # JSONB, NOT JSON - and that is not a style preference.
    #
    # Postgres's `json` type stores the raw text and HAS NO EQUALITY OPERATOR. So
    # `SELECT '{}'::json = '{}'` is a hard error - which meant Alembic's autogenerate,
    # which compares server defaults, could not run at all:
    #
    #     ProgrammingError: operator does not exist: json = unknown
    #
    # The migration tool was broken by the column type. JSONB stores parsed binary,
    # supports equality and containment, and can be indexed. There is no reason to
    # prefer `json` here and one very concrete reason not to.
    # NOTE text(), not a bare string. A raw string gets re-quoted on its way into
    # the DDL comparison and comes back out as an unterminated literal:
    #     SyntaxError: unterminated quoted string at or near "' AS anon_1"
    # text() says "this is SQL, pass it through".
    components: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    top_features: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )

    # --- workflow -----------------------------------------------------------
    assigned_to_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("security_users.id"), nullable=True, index=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    acknowledged_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("security_users.id"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("security_users.id"), nullable=True
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow
    )

    notes: Mapped[list[AlertNote]] = relationship(
        back_populates="alert", cascade="all, delete-orphan", order_by="AlertNote.id"
    )


class AlertNote(Base):
    """An analyst's working notes on an alert.

    Append-only, and never edited. An investigation record that can be silently
    rewritten after the fact is not a record - it is a draft, and it is worthless the
    moment anyone needs to rely on it. If an analyst was wrong at 14:00 and right at
    16:00, both belong in the file: that is what makes it an audit trail rather than
    a story.
    """

    __tablename__ = "alert_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("alerts.id", ondelete="CASCADE"), index=True
    )
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("security_users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now()
    )

    alert: Mapped[Alert] = relationship(back_populates="notes")


class MaliciousEventDay(Base):
    """The days on which a malicious event ACTUALLY occurred.

    THIS IS A DIFFERENT ANSWER KEY FROM insiders.csv, AND THE DIFFERENCE IS 49%.

    `insiders.csv` gives each insider a WINDOW - a start and an end. Labelling every
    day in that window as malicious is the obvious reading, and it is what this
    project did. It is also what produces 1,892 malicious user-days.

    But CERT also ships PER-INSIDER EVENT FILES (answers/r4.2-1/, -2/, -3/) listing
    the actual malicious events with timestamps. Count only the days those events
    fall on and you get 966 - which is the number the published literature reports.

    926 of our "malicious" days - 49% of them - contain NO MALICIOUS ACTIVITY.

    AND THE ERROR IS NOT EVENLY SPREAD, WHICH IS WHAT MAKES IT DANGEROUS:

        scenario 1:  196 window days ->  85 real   (2.3x inflated)
        scenario 2: 1676 window days -> 861 real   (1.9x inflated)
        scenario 3:   20 window days ->  20 real   (exact)

    Scenario 1 is a SINGLE-DAY exfiltration handed a multi-week window. AAM0658 has
    seven window days and two real ones - so the detector is being scored for
    "missing" five days on which he did nothing wrong. That is precisely why our
    scenario-1 recall looks like 73% and our scenario-2 recall looks like 97%.

    Both conventions are now stored and both are REPORTED. Not because one is a lie -
    the window is a defensible thing to want to detect ("catch him during the
    campaign") - but because comparing our numbers to a published paper's without
    saying which convention produced them is how benchmarks become fiction.
    """

    __tablename__ = "malicious_event_days"
    __table_args__ = (
        UniqueConstraint("user_id", "event_date", name="uq_malicious_event_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(20), index=True)
    event_date: Mapped[datetime] = mapped_column(Date, index=True)
    scenario: Mapped[int] = mapped_column(Integer, index=True)

    # How many malicious events that day. A day with one wikileaks upload and a day
    # with forty file copies are both "malicious", and they are not the same day.
    event_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")