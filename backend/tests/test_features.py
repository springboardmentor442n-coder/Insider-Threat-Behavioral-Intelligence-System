"""Tests for the feature-engineering layer.

These verify the STRUCTURE and INVARIANTS of the pipeline. They do not assert
on specific counts, because those depend on which dataset is loaded - and a test
that only passes against one particular database is not a test, it is a
coincidence.

The invariants below are the ones that, if violated, silently ruin every
downstream result. A wrong count is visible. A leaking label is not.
"""

import pytest
from sqlalchemy import text

from backend.app.database import SessionLocal


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _has_features(db) -> bool:
    n = db.execute(text("SELECT COUNT(*) FROM daily_features")).scalar()
    return bool(n)


def test_no_negative_counts(db) -> None:
    """Every feature is a count. A negative count means the SQL is wrong."""
    if not _has_features(db):
        pytest.skip("no features built - run scripts.build_features")

    bad = db.execute(text("""
        SELECT COUNT(*) FROM daily_features
        WHERE logon_count < 0 OR usb_connect_count < 0 OR file_event_count < 0
           OR email_count < 0 OR http_total_visits < 0
    """)).scalar()
    assert bad == 0


def test_after_hours_never_exceeds_total_logons(db) -> None:
    """A subset cannot be larger than the set it is drawn from.

    after_hours_logon_count counts a SUBSET of logon_count. If it ever exceeds
    it, the two are being computed against different populations - a genuine bug
    that would otherwise pass unnoticed.
    """
    if not _has_features(db):
        pytest.skip("no features built")

    bad = db.execute(text("""
        SELECT COUNT(*) FROM daily_features
        WHERE after_hours_logon_count > logon_count
    """)).scalar()
    assert bad == 0


def test_external_emails_never_exceed_total_emails(db) -> None:
    if not _has_features(db):
        pytest.skip("no features built")

    bad = db.execute(text("""
        SELECT COUNT(*) FROM daily_features
        WHERE external_email_count > email_count
    """)).scalar()
    assert bad == 0


def test_one_row_per_user_per_day(db) -> None:
    """The grain must actually hold. Duplicate user-days would double-count."""
    if not _has_features(db):
        pytest.skip("no features built")

    dupes = db.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT user_id, date FROM daily_features
            GROUP BY user_id, date HAVING COUNT(*) > 1
        ) t
    """)).scalar()
    assert dupes == 0


def test_only_insiders_have_malicious_days(db) -> None:
    """A non-insider must never have a day labelled malicious.

    If this fails, the ground-truth join is wrong and the labels are garbage -
    which would make every precision/recall number in the final report a lie.
    """
    if not _has_features(db):
        pytest.skip("no features built")

    bad = db.execute(text("""
        SELECT COUNT(*)
        FROM daily_features f
        JOIN employees e ON e.user_id = f.user_id
        WHERE f.is_malicious AND NOT e.is_insider
    """)).scalar()
    assert bad == 0


def test_insiders_also_have_normal_days(db) -> None:
    """An insider's whole history must NOT be labelled malicious.

    This is the subtle one. Every r4.2 insider behaved normally for months before
    they turned - only the days inside their answer-key window are malicious.
    Labelling their entire history as bad would teach the model that ordinary
    behaviour is an attack, which is worse than not training at all.
    """
    if not _has_features(db):
        pytest.skip("no features built")

    insiders = db.execute(text("""
        SELECT COUNT(*) FROM employees WHERE is_insider
    """)).scalar()
    if not insiders:
        pytest.skip("no insiders loaded")

    all_bad = db.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT f.user_id
            FROM daily_features f
            JOIN employees e ON e.user_id = f.user_id
            WHERE e.is_insider
            GROUP BY f.user_id
            HAVING BOOL_AND(f.is_malicious)   -- every single day malicious
        ) t
    """)).scalar()
    assert all_bad == 0, "an insider has NO normal days - the labelling window is wrong"


def test_baselines_exclude_malicious_days(db) -> None:
    """The contamination guard must actually be in force.

    A baseline built from the attack days is worse than useless: the insider's own
    spike raises his own average, so he looks less anomalous the worse he behaves.
    """
    if not _has_features(db):
        pytest.skip("no features built")

    baselines = db.execute(text("SELECT COUNT(*) FROM user_baselines")).scalar()
    if not baselines:
        pytest.skip("no baselines built")

    # Every baseline must be built from at least one day, and training_days must
    # never exceed that user's count of NON-malicious days.
    bad = db.execute(text("""
        SELECT COUNT(*)
        FROM user_baselines b
        JOIN (
            SELECT user_id, COUNT(*) AS clean_days
            FROM daily_features WHERE NOT is_malicious
            GROUP BY user_id
        ) c ON c.user_id = b.user_id
        WHERE b.training_days > c.clean_days OR b.training_days < 1
    """)).scalar()
    assert bad == 0


def test_no_baseline_statistics_leak_into_the_model() -> None:
    """Baseline stats must NEVER be fed to the model as features.

    THIS TEST EXISTS BECAUSE THE LEAK ACTUALLY HAPPENED.

    add_deviation_features() merges per-user baseline statistics into the frame as
    columns named `<feature>__user_mean` / `<feature>__user_std`, uses them to
    compute z-scores, and then DELETES them. That deletion is the point of this
    test.

    Originally they were left in the frame and filtered out downstream. A prefix
    match on "roll7_" / "roll14_" scooped them straight into the model matrix
    anyway. They are not features - they are per-user CONSTANTS, a description of
    who the person IS rather than what they DID. Handing them to the classifier
    invites it to learn "people with a high baseline are insiders", which is a
    spurious correlation wearing a signal's clothes.

    The tell was the metrics: XGBoost reported precision 0.9936 and recall 1.0000.
    On a 0.5% class imbalance those numbers are not an achievement, they are a
    confession. No test caught it - only reading the feature importances did.

    The fix is now structural rather than defensive: the columns are DELETED once
    they have served their purpose, so there is nothing left to leak. A guard you
    must remember to apply is worse than a mistake you cannot make.
    """
    import numpy as np
    import pandas as pd

    from backend.app.detection import (
        COUNT_FEATURES,
        FLAG_FEATURES,
        add_deviation_features,
        add_temporal_features,
        build_deviation_matrix,
        build_model_matrix,
    )

    # A tiny synthetic frame with the same SHAPE as the real one.
    n_users, n_days = 4, 40
    rng = np.random.RandomState(0)
    rows = []
    base = pd.Timestamp("2010-01-04")
    for u in range(n_users):
        for d in range(n_days):
            row = {
                "user_id": f"U{u:03d}",
                "date": base + pd.Timedelta(days=d),
                "department": "1 - Software",
                "is_malicious": False,
            }
            for f in COUNT_FEATURES:
                row[f] = int(rng.poisson(2))
            for f in FLAG_FEATURES:
                row[f] = False
            rows.append(row)
    df = pd.DataFrame(rows)

    df = add_temporal_features(df)
    df = add_deviation_features(df, training_cutoff=base + pd.Timedelta(days=20))

    # The z-scores must have been computed - otherwise the baselines were never
    # used and this test is checking nothing.
    assert any(c.startswith("z_") for c in df.columns), "no z-scores computed"
    assert any(c.startswith("z_roll") for c in df.columns), "no temporal z-scores"

    # And the baseline statistics themselves must be GONE - deleted, not merely
    # filtered downstream.
    survivors = [c for c in df.columns if "__user_" in c or "__peer_" in c]
    assert not survivors, (
        f"baseline statistics survived into the frame: {survivors[:5]}. "
        "They must be dropped once the z-scores are computed - leaving them "
        "present is what let them leak into the model in the first place."
    )

    # Belt and braces: nothing with a '__' in the name reaches either model.
    _X, _y, cols = build_model_matrix(df)
    leaked = [c for c in cols if "__" in c]
    assert not leaked, f"baseline statistics leaked into the model matrix: {leaked[:5]}"

    _X_iso, iso_cols = build_deviation_matrix(df)
    leaked_iso = [c for c in iso_cols if "__" in c]
    assert not leaked_iso, f"baseline stats leaked into Isolation Forest: {leaked_iso[:5]}"


def test_rolling_features_do_not_see_the_future() -> None:
    """Rolling windows must be TRAILING. A leaking window is undetectable in the
    metrics - it just makes them beautiful - so it has to be tested directly.

    Construct a user who does nothing for 10 days and then spikes. If the rolling
    mean on day 5 is nonzero, the window is looking forward, and every temporal
    result in this project would be worthless.
    """
    import numpy as np
    import pandas as pd

    from backend.app.detection import COUNT_FEATURES, add_temporal_features

    base = pd.Timestamp("2010-01-04")
    rows = []
    for d in range(20):
        row = {
            "user_id": "U000",
            "date": base + pd.Timedelta(days=d),
            "department": "1 - Software",
            "is_malicious": False,
        }
        for f in COUNT_FEATURES:
            row[f] = 0
        # the spike happens ONLY on day 10 and after
        row["usb_connect_count"] = 100 if d >= 10 else 0
        rows.append(row)

    df = add_temporal_features(pd.DataFrame(rows))
    df = df.sort_values("date").reset_index(drop=True)

    # Days 0-9 precede the spike. Their rolling means MUST be zero.
    before = df.iloc[:10]
    assert (before["roll7_usb_connect_count"] == 0).all(), (
        "rolling window is seeing the FUTURE - the spike on day 10 is bleeding "
        "backwards. Every temporal metric in this project would be invalid."
    )
    assert (before["roll14_usb_connect_count"] == 0).all()

    # And day 10 onward must actually register it.
    assert df.iloc[10]["roll7_usb_connect_count"] > 0


def test_build_features_recreates_its_tables_so_schema_changes_apply() -> None:
    """Rebuilding features must rebuild ONLY the derived tables - and never
    reach for create_all(), which is what caused the original bug twice.

    HISTORY, BECAUSE IT MATTERS
    ---------------------------
    `Base.metadata.create_all()` creates missing tables. It does not ALTER existing
    ones. So adding a column to a model whose table already existed gave a clean
    startup followed by a crash on the first INSERT:

        column "session_count" of relation "daily_features" does not exist

    That happened twice. First when http_daily_summary gained wikileaks_visits -
    and it blew up AFTER seven minutes of streaming 13.9 GB of http.csv. Then again
    when daily_features gained session_count, because the fix had been wired into
    the ingestion script and not the features script. A fix applied in one place is
    not a fix.

    The schema is now owned by ALEMBIC. This function's remaining job is much
    narrower: drop and rebuild two DERIVED tables whose CONTENT is stale. It must
    not touch the schema of anything else, and it must not touch
    http_daily_summary - which is derived too, but costs a 13.9 GB re-stream to
    rebuild.

    Verified with mocks: an earlier version of this test called the real function
    and silently DROPPED the developer's 330,000-row daily_features table on every
    pytest run. conftest.py says in as many words that tests must not do that.
    """
    from unittest.mock import patch

    from backend.app import features
    from backend.app.database import engine
    from backend.app.features_models import DailyFeatures, UserBaseline
    from backend.app.models import HttpDailySummary

    with (
        patch.object(DailyFeatures.__table__, "drop") as drop_features,
        patch.object(UserBaseline.__table__, "drop") as drop_baselines,
        patch.object(HttpDailySummary.__table__, "drop") as drop_http,
        patch.object(DailyFeatures.__table__, "create") as create_features,
        patch.object(UserBaseline.__table__, "create") as create_baselines,
        patch("backend.app.database.Base.metadata.create_all") as create_all,
    ):
        features.recreate_feature_tables(engine)

    # The two derived tables must be dropped and rebuilt.
    assert drop_features.called, "daily_features was not dropped"
    assert drop_baselines.called, "user_baselines was not dropped"
    assert create_features.called, "daily_features was dropped but never rebuilt"
    assert create_baselines.called, "user_baselines was dropped but never rebuilt"

    # http_daily_summary must survive. It is built by streaming 13.9 GB of
    # http.csv - roughly seven minutes. Dropping it would silently force a full
    # re-ingest on someone who only asked to rebuild features.
    assert not drop_http.called, (
        "recreate_feature_tables dropped http_daily_summary. It must not: "
        "rebuilding that table costs a 13.9 GB re-stream of http.csv."
    )

    # And it must NOT call create_all(). That function is the original sin here:
    # it would silently create any table that happens to be missing, papering over
    # a database that was never migrated, and it would ignore any table that exists
    # but is out of date. The schema belongs to Alembic now.
    assert not create_all.called, (
        "recreate_feature_tables called Base.metadata.create_all(). It must not - "
        "create_all() cannot ALTER an existing table, which is the bug that broke "
        "this build twice. Schema changes go through Alembic migrations."
    )


def test_build_features_script_actually_calls_the_recreate() -> None:
    """The function above is useless if the script never calls it.

    That is precisely how this bug survived the first fix: recreate_derived_tables
    existed, was correct, and was wired into exactly one of the two scripts that
    needed it.
    """
    import inspect

    from scripts import build_features

    src = inspect.getsource(build_features.main)
    assert "recreate_feature_tables" in src, (
        "build_features.main() does not call recreate_feature_tables. Any new "
        "column on DailyFeatures will fail at INSERT time with 'column ... does "
        "not exist'. This has already happened twice."
    )