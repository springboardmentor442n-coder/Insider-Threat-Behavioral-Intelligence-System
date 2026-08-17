"""Feature engineering, UEBA scoring and model behaviour."""

import numpy as np
import pandas as pd
import pytest

from app.ml import ueba
from app.ml.features import (
    BEHAVIOURAL_COLUMNS,
    FEATURE_COLUMNS,
    _device_features,
    _email_features,
    _file_features,
    _logon_features,
    heuristic_labels,
)
from config import Config
from tests.conftest import needs_model


# ── feature engineering ────────────────────────────────────────────────────
def test_logon_features_counts_only_logon_events_and_flags_off_hours():
    logon = pd.DataFrame({
        "date": pd.to_datetime([
            "2010-03-01 08:00", "2010-03-01 19:30",   # 1 Logon in hours, 1 off-hours
            "2010-03-01 17:00", "2010-03-01 03:00",   # Logoff rows
        ]),
        "user": ["U1"] * 4,
        "pc": ["PC-1", "PC-2", "PC-1", "PC-2"],
        "activity": ["Logon", "Logon", "Logoff", "Logoff"],
    })
    out = _logon_features(logon).iloc[0]

    assert out["logon_count"] == 2          # Logoff rows excluded
    assert out["off_hours_logons"] == 2     # 19:30 and 03:00
    assert out["distinct_pcs"] == 2


def test_device_features_ignore_disconnects():
    device = pd.DataFrame({
        "date": pd.to_datetime(["2010-03-01 09:00", "2010-03-01 22:00", "2010-03-01 23:00"]),
        "user": ["U1"] * 3,
        "pc": ["PC-1"] * 3,
        "activity": ["Connect", "Connect", "Disconnect"],
    })
    out = _device_features(device).iloc[0]

    assert out["usb_connects"] == 2
    assert out["off_hours_usb"] == 1


def test_file_features_flag_sensitive_extensions():
    files = pd.DataFrame({
        "date": pd.to_datetime(["2010-03-01 09:00"] * 4),
        "user": ["U1"] * 4,
        "filename": ["a.doc", "b.PDF", "c.zip", "d.jpg"],
    })
    out = _file_features(files).iloc[0]

    assert out["files_copied_to_usb"] == 4
    assert out["sensitive_files_to_usb"] == 3  # case-insensitive, jpg excluded


def test_email_features_classify_external_recipients():
    email = pd.DataFrame({
        "date": pd.to_datetime(["2010-03-01 09:00"] * 3),
        "user": ["U1"] * 3,
        "to": ["a@dtaa.com", "b@gmail.com", "c@dtaa.com"],
        "size": [100, 200, 300],
        "attachment_count": [0, 2, 1],
    })
    out = _email_features(email).iloc[0]

    assert out["total_emails_sent"] == 3
    assert out["external_emails_sent"] == 1
    assert out["total_attachments"] == 3
    assert out["total_email_size"] == 600


def test_email_features_tolerate_missing_attachment_column():
    email = pd.DataFrame({
        "date": pd.to_datetime(["2010-03-01 09:00"]),
        "user": ["U1"],
        "to": ["a@dtaa.com"],
        "size": [100],
    })
    out = _email_features(email).iloc[0]
    assert out["total_attachments"] == 0


def test_heuristic_labels_flag_only_extreme_days():
    rng = np.random.default_rng(0)
    df = pd.DataFrame(
        {c: rng.integers(0, 3, 400).astype(float) for c in BEHAVIOURAL_COLUMNS}
    )
    df.loc[0, ["files_copied_to_usb", "off_hours_logons"]] = [200, 50]

    labels = heuristic_labels(df)
    assert labels.iloc[0] == 1
    assert labels.sum() < len(df) * 0.1  # stays rare


# ── UEBA engine ────────────────────────────────────────────────────────────
@pytest.fixture()
def toy_baselines():
    history = pd.DataFrame({
        "user": ["U1"] * 20,
        **{c: [1.0] * 20 for c in BEHAVIOURAL_COLUMNS},
    })
    return ueba.build_baselines(history)


def test_behavioural_score_is_zero_at_baseline(toy_baselines):
    row = pd.DataFrame([{"user": "U1", **{c: 1.0 for c in BEHAVIOURAL_COLUMNS}}])
    assert ueba.behavioural_score(row, toy_baselines)[0] == pytest.approx(0.0)


def test_behavioural_score_saturates_at_100(toy_baselines):
    row = pd.DataFrame([{"user": "U1", **{c: 9999.0 for c in BEHAVIOURAL_COLUMNS}}])
    assert ueba.behavioural_score(row, toy_baselines)[0] == pytest.approx(100.0)


def test_score_is_bounded_and_monotonic_in_usb_activity(toy_baselines):
    scores = []
    for value in [1, 3, 6, 12, 40]:
        row = pd.DataFrame([{
            "user": "U1",
            **{c: 1.0 for c in BEHAVIOURAL_COLUMNS},
            "files_copied_to_usb": float(value),
        }])
        scores.append(ueba.behavioural_score(row, toy_baselines)[0])

    assert scores == sorted(scores)
    assert all(0.0 <= s <= 100.0 for s in scores)


def test_unknown_user_falls_back_to_population_baseline(toy_baselines):
    row = pd.DataFrame([{"user": "GHOST", **{c: 5.0 for c in BEHAVIOURAL_COLUMNS}}])
    score = ueba.behavioural_score(row, toy_baselines)[0]
    assert 0.0 <= score <= 100.0  # no KeyError, no NaN


def test_weights_are_respected(toy_baselines):
    """A 3x indicator must move the score more than a 2x one."""
    def score_for(feature):
        row = pd.DataFrame([{
            "user": "U1",
            **{c: 1.0 for c in BEHAVIOURAL_COLUMNS},
            feature: 100.0,
        }])
        return ueba.behavioural_score(row, toy_baselines)[0]

    assert score_for("files_copied_to_usb") > score_for("off_hours_logons")


def test_severity_bands_match_the_documented_thresholds():
    assert ueba.severity(95) == "CRITICAL"
    assert ueba.severity(80) == "CRITICAL"
    assert ueba.severity(79.9) == "HIGH"
    assert ueba.severity(60) == "HIGH"
    assert ueba.severity(59.9) == "MEDIUM"
    assert ueba.severity(40) == "MEDIUM"
    assert ueba.severity(39.9) == "LOW"
    assert ueba.severity(0) == "LOW"


def test_severity_series_matches_scalar_severity():
    scores = np.array([0, 39.9, 40, 59.9, 60, 79.9, 80, 100])
    assert list(ueba.severity_series(scores)) == [ueba.severity(s) for s in scores]


def test_composite_score_blends_both_signals():
    ueba_only = ueba.composite_score(np.array([100.0]), np.array([0.0]))[0]
    ml_only = ueba.composite_score(np.array([0.0]), np.array([1.0]))[0]

    assert ueba_only == pytest.approx(Config.UEBA_WEIGHT * 100)
    assert ml_only == pytest.approx(Config.ML_WEIGHT * 100)
    assert ueba.composite_score(np.array([100.0]), np.array([1.0]))[0] == pytest.approx(100.0)


def test_deviation_report_covers_every_behaviour(toy_baselines):
    row = pd.Series({"user": "U1", **{c: 4.0 for c in BEHAVIOURAL_COLUMNS}})
    report = ueba.deviation_report(row, toy_baselines, pd.Series(dtype=float))

    assert {d["feature"] for d in report} == set(BEHAVIOURAL_COLUMNS)
    # Sorted by deviation, strongest first.
    sigmas = [d["deviation_sigma"] for d in report]
    assert sigmas == sorted(sigmas, reverse=True)


# ── trained model ──────────────────────────────────────────────────────────
@needs_model
def test_model_separates_known_insider_days_from_benign_ones(app):
    from app.ml import engine as eng

    with app.app_context():
        engine = eng.get_engine()
        df = engine.df
        if df["is_insider"].sum() == 0:
            pytest.skip("dataset carries no ground-truth labels")

        mal = df[df["is_insider"] == 1]["ml_probability"].mean()
        ben = df[df["is_insider"] == 0]["ml_probability"].mean()
        assert mal > ben * 5, f"weak separation: malicious {mal:.3f} vs benign {ben:.3f}"


@needs_model
def test_scored_columns_are_within_range(app):
    from app.ml import engine as eng

    with app.app_context():
        df = eng.get_engine().df
        assert df["risk_score"].between(0, 100).all()
        assert df["ueba_score"].between(0, 100).all()
        assert df["ml_probability"].between(0, 1).all()
        assert set(df["severity"]) <= {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


@needs_model
def test_score_record_fills_gaps_from_the_user_baseline(app, sample_user):
    from app.ml import engine as eng

    with app.app_context():
        engine = eng.get_engine()
        result = engine.score_record(sample_user, {"files_copied_to_usb": 25.0})

        assert result["baseline_source"] == "user"
        assert result["supplied_features"] == ["files_copied_to_usb"]
        assert len(result["defaulted_features"]) == len(FEATURE_COLUMNS) - 1
        # Nothing silently zeroed: logons come from the baseline, not 0.
        assert result["inputs"]["logon_count"] > 0
