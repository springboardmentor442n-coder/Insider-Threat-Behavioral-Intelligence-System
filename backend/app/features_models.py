"""Phase 3 models: engineered features and per-user behavioural baselines.

Kept in their own module rather than bolted onto models.py because they are a
different KIND of thing. models.py holds raw ingested facts - what happened.
These hold DERIVED state - what we computed about what happened. If the feature
definitions change, this is what gets recomputed; the raw events never move.
"""

from __future__ import annotations

from datetime import date as date_type

from sqlalchemy import BigInteger, Boolean, Date, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class DailyFeatures(Base):
    """One row per user, per day they were active. The model's input.

    WHY THIS GRAIN?

    Not per-event: a single logon tells you nothing. "Logged on at 02:14" is
    only suspicious in the context of the other 500 days where they logged on at
    09:00. Anomaly detection needs a subject with a history, and the natural
    subject here is a user-day.

    Not per-user-overall: aggregating 17 months into one row per user destroys
    the timeline. Scenario 2's insider behaved perfectly normally for months and
    then turned. Collapse that to a single average and the spike vanishes into
    the mean - you would be detecting nothing.

    A user-day is the smallest unit that still carries behavioural context. Every
    feature below is a count or a flag scoped to one person on one day.

    Each feature exists because a specific r4.2 scenario would produce it. This
    is not a grab-bag of everything the data could yield - it is targeted at the
    three attacks the answer key says are actually in here.
    """

    __tablename__ = "daily_features"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("employees.user_id"), index=True)
    date: Mapped[date_type] = mapped_column(Date, index=True)

    # --- Logon -------------------------------------------------------------
    logon_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Scenario 1: "a user who has not previously used removable drives or worked
    # after hours begins doing both". After-hours activity is half of that
    # signal. Defined as before 07:00 or at/after 18:00.
    after_hours_logon_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    weekend_logon_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    distinct_pcs: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # --- Session duration (from logon/logoff pairs) -------------------------
    #
    # MEASURED, not assumed. On the real CERT data, lift at z>2 vs normal days:
    #
    #   total_session_hours   scenario 1:  34x   scenario 2: 0.9x   scenario 3:  99x
    #   session_count         scenario 1:  28x   scenario 2: 0.4x   scenario 3:  19x
    #   max_session_hours     scenario 1:   8x   scenario 2: 1.8x   scenario 3: 0.0x
    #
    # total_session_hours is the single strongest signal for scenario 3 in the
    # whole feature set - the sysadmin plants his keylogger during long evening
    # sessions. max_session_hours was measured and DROPPED: it carries almost no
    # signal, and a feature that does nothing is not free, it is noise.
    session_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    total_session_hours: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")

    # Scenario 3: the sysadmin plants a keylogger on his SUPERVISOR's machine.
    # A logon to a PC this user has never touched before is the observable trace
    # of that. Computed as the first date each (user, pc) pair ever appears.
    new_pc_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Scenario 3, sharpened. Not just "a new PC" but "his supervisor's PC",
    # resolved through the LDAP reporting line. This is the single most specific
    # feature in the set - a normal employee essentially never logs into their
    # boss's machine.
    used_supervisor_pc: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # --- Device / USB ------------------------------------------------------
    # Every one of the three scenarios involves a thumb drive. This is the
    # highest-signal family of features in the dataset.
    usb_connect_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    after_hours_usb_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    weekend_usb_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # --- File --------------------------------------------------------------
    file_event_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Scenario 3: the keylogger itself. An .exe written to removable media is
    # rare and specific.
    exe_file_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    doc_file_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    zip_file_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # --- Email -------------------------------------------------------------
    email_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Exfiltration by email: any recipient outside dtaa.com.
    external_email_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    total_email_size: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    total_attachments: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Scenario 3 ends with "sends out an alarming mass email". Fan-out is the
    # signal, so we keep the MAX recipient count of the day, not the mean -
    # averaging would bury one 200-recipient blast among fifty normal 2-person
    # emails.
    max_recipients: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # --- HTTP (from the aggregated summary) --------------------------------
    http_total_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    job_site_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")       # scenario 2
    wikileaks_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")      # scenario 1
    cloud_storage_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # weak
    hacking_site_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0")   # scenario 3
    distinct_domains: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # --- Label -------------------------------------------------------------
    # TRUE only for days inside the insider's malicious WINDOW, not for every day
    # of an insider's life. A scenario-2 insider was a normal employee for months
    # before he turned; labelling his early days malicious would teach the model
    # that normal behaviour is malicious, which is worse than useless.
    # --- TWO LABELS, AND THEY DISAGREE ABOUT 49% OF THE MALICIOUS DAYS -------
    #
    # is_malicious        : the day falls inside the insider's WINDOW (insiders.csv
    #                       start -> end). 1,892 days.
    # has_malicious_event : a malicious event ACTUALLY happened that day, per CERT's
    #                       per-insider answer files. 966 days - and this is the
    #                       convention the published literature uses.
    #
    # Neither is wrong. "Catch him during the campaign" is a defensible target, and so
    # is "catch him on the day he did it". But quoting a recall number without saying
    # WHICH ONE produced it makes it incomparable to anything, including itself.
    #
    # Both are stored. Both are reported. NEITHER is a model input - they are the exam
    # answer key, and feeding them to the model would be target leakage.
    is_malicious: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)
    has_malicious_event: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", index=True
    )

    __table_args__ = (
        Index("ix_features_user_date", "user_id", "date", unique=True),
    )


class UserBaseline(Base):
    """What "normal" looks like for one specific person.

    This is the idea the whole platform rests on. "Connected a USB drive" is not
    suspicious. "Connected a USB drive, having never connected one in eight
    months" is scenario 1, verbatim. The difference between those two statements
    is this table.

    Stored as mean and standard deviation per feature, computed over a TRAINING
    WINDOW (the first N days) rather than over all time. That ordering matters:
    if the baseline included the attack days, the attack would inflate the very
    average it is supposed to stand out from - the model would be grading itself
    on a curve it drew after seeing the answers.

    A z-score of (today - mean) / std then says, in units of that person's own
    variability, how far outside their normal today is.
    """

    __tablename__ = "user_baselines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("employees.user_id"), unique=True, index=True
    )

    # How much history this baseline was built from. A baseline from 3 days is
    # not worth the bytes it occupies, and we need to know that when scoring.
    training_days: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Peer group, carried from LDAP. Lets us ask the second question:
    # not just "is this odd for HIM", but "is this odd for a SALESMAN".
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)

    mean_logon_count: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    std_logon_count: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")

    mean_after_hours_logon: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    std_after_hours_logon: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")

    mean_usb_connect: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    std_usb_connect: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")

    mean_file_events: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    std_file_events: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")

    mean_external_email: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    std_external_email: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")

    mean_http_visits: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    std_http_visits: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")

    # Booleans that encode "this person has NEVER done X". Scenario 1 turns on
    # exactly this: a user who never used USB and never worked late suddenly does
    # both. A z-score cannot express that cleanly when the standard deviation is
    # zero, so we record the fact directly.
    ever_used_usb: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    ever_worked_after_hours: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")