"""Tests for the Risk Scoring Engine (spec Module 6) and SHAP explanations.

The important test in this file is test_prior_alerts_cannot_see_today. Everything
else is arithmetic; that one is the difference between a feature and a leak.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backend.app.risk import (
    THRESHOLDS,
    WEIGHTS,
    RiskLevel,
    compute_components,
    compute_prior_alerts,
    level_for,
    score,
)


def test_the_weights_sum_to_one() -> None:
    """35 + 25 + 20 + 10 + 10 = 100. If they don't, the score isn't 0-100."""
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_prior_alerts_cannot_see_today() -> None:
    """THE LEAK TEST. This is the one that matters.

    `historical_security_events` asks "has this user been flagged BEFORE?". If
    today's own alert counts toward today's prior-alert score, the system is scoring
    itself: the model flags a day, that flag inflates the same day's risk, and the
    risk score reports a confidence it did not earn.

    It is circular. It is INVISIBLE in the metrics - everything simply looks better.
    And it is one of the most common ways a security ML system ends up quietly
    marking its own homework.

    The defence is one `.shift(1)` before the rolling window. This test is what keeps
    it there.
    """
    df = pd.DataFrame({
        "user_id": ["A"] * 5,
        "date": pd.date_range("2010-01-01", periods=5),
    })
    # Day 0 is flagged. Nothing else is.
    prob = np.array([0.99, 0.0, 0.0, 0.0, 0.0])

    prior = compute_prior_alerts(df, prob, alert_threshold=0.5, window_days=30)

    assert prior.iloc[0] == 0.0, (
        "DAY 0 CAN SEE ITS OWN ALERT. The risk score is now counting today's flag as "
        "evidence for today's flag - it is scoring itself, and every metric will "
        "quietly improve while the system learns nothing."
    )
    # But every LATER day must see it.
    assert prior.iloc[1] == 1.0
    assert prior.iloc[4] == 1.0


def test_prior_alerts_do_not_bleed_between_users() -> None:
    """User B must not inherit user A's history."""
    df = pd.DataFrame({
        "user_id": ["A", "A", "B", "B"],
        "date": pd.to_datetime(["2010-01-01", "2010-01-02"] * 2),
    })
    prob = np.array([0.99, 0.0, 0.0, 0.0])

    prior = compute_prior_alerts(df, prob)

    assert prior.iloc[1] == 1.0, "A's second day should see A's first-day alert"
    assert prior.iloc[3] == 0.0, (
        "B inherited A's alert history. The groupby is broken, and every user's risk "
        "is now contaminated by whoever happens to sit next to them in the frame."
    )


def test_prior_alerts_respect_the_window() -> None:
    """An alert 90 days ago is not evidence about today."""
    df = pd.DataFrame({
        "user_id": ["A"] * 40,
        "date": pd.date_range("2010-01-01", periods=40),
    })
    prob = np.zeros(40)
    prob[0] = 0.99   # flagged on day 0 only

    prior = compute_prior_alerts(df, prob, window_days=10)

    assert prior.iloc[5] == 1.0, "within the window, the alert should count"
    assert prior.iloc[30] == 0.0, (
        "an alert 30 days ago is still counted with a 10-day window - the rolling "
        "window is not bounded"
    )


def test_components_are_bounded() -> None:
    """Every component must land in 0-100, or the weighted total is not 0-100."""
    n = 50
    rng = np.random.RandomState(0)
    df = pd.DataFrame({
        "user_id": [f"U{i}" for i in range(n)],
        "date": pd.date_range("2010-01-01", periods=n),
        "used_supervisor_pc": rng.randint(0, 2, n),
        "wikileaks_visits": rng.randint(0, 5, n),
        # z-scores are clipped at 25 in the pipeline, so feed the extremes
        "z_usb_connect_count": rng.uniform(-25, 25, n),
        "z_file_event_count": rng.uniform(-25, 25, n),
        "z_after_hours_logon_count": rng.uniform(-25, 25, n),
        "z_hacking_site_visits": rng.uniform(-25, 25, n),
        "z_exe_file_count": rng.uniform(-25, 25, n),
    })
    prob = rng.uniform(0, 1, n)

    comp = compute_components(df, prob, prior_alerts=pd.Series(rng.randint(0, 20, n)))

    for name in WEIGHTS:
        v = comp[name].to_numpy()
        assert v.min() >= 0.0, f"{name} went below 0: {v.min()}"
        assert v.max() <= 100.0, f"{name} exceeded 100: {v.max()}"


def test_the_total_is_the_weighted_sum() -> None:
    """The score must actually BE the sum of its parts.

    A decomposed score whose parts do not add up to the whole is worse than an opaque
    one: it teaches an analyst to distrust the arithmetic, and then they distrust
    everything else too.
    """
    n = 20
    rng = np.random.RandomState(1)
    df = pd.DataFrame({
        "user_id": [f"U{i}" for i in range(n)],
        "date": pd.date_range("2010-01-01", periods=n),
        "used_supervisor_pc": rng.randint(0, 2, n),
        "wikileaks_visits": rng.randint(0, 3, n),
        "z_usb_connect_count": rng.uniform(0, 10, n),
        "z_after_hours_logon_count": rng.uniform(0, 10, n),
    })
    prob = rng.uniform(0, 1, n)

    r = score(df, prob, prior_alerts=pd.Series(np.zeros(n)))

    for i in range(n):
        parts = sum(r[f"w_{name}"].iloc[i] for name in WEIGHTS)
        assert abs(parts - r["risk_score"].iloc[i]) < 1e-6, (
            "the components do not sum to the total"
        )


def test_levels_bucket_correctly() -> None:
    assert level_for(100) is RiskLevel.CRITICAL
    assert level_for(THRESHOLDS[RiskLevel.CRITICAL]) is RiskLevel.CRITICAL
    assert level_for(THRESHOLDS[RiskLevel.CRITICAL] - 0.1) is RiskLevel.HIGH
    assert level_for(THRESHOLDS[RiskLevel.HIGH]) is RiskLevel.HIGH
    assert level_for(THRESHOLDS[RiskLevel.MEDIUM]) is RiskLevel.MEDIUM
    assert level_for(0) is RiskLevel.LOW


def test_the_specs_original_thresholds_could_not_fire() -> None:
    """DOCUMENTS THE FINDING, so nobody quietly puts them back.

    The spec says CRITICAL = 80. The single largest component (behavioral_anomalies)
    carries a 35% weight, so even a model that is COMPLETELY CERTAIN contributes 35
    points. To reach 80, several components must fire at once - and real insiders
    trigger one or two, not five.

    A scenario-1 insider never touches his supervisor's PC. A scenario-3 sysadmin
    never browses job sites. Measured on the real labels, the spec's thresholds
    produced ZERO critical alerts and 0 of 21 insiders at HIGH or above.
    """
    SPEC_CRITICAL = 80

    # A model that is certain, and a strong data-access signal, and nothing else -
    # which is exactly what a scenario-1 or scenario-2 insider looks like.
    realistic_best = (
        100 * WEIGHTS["behavioral_anomalies"]
        + 100 * WEIGHTS["data_access_violations"]
        + 100 * WEIGHTS["access_pattern_deviations"]
    )
    assert realistic_best < SPEC_CRITICAL, (
        "the premise of this test has changed - re-examine the finding"
    )

    # And with our calibrated thresholds, that same insider IS critical.
    assert level_for(realistic_best) is RiskLevel.CRITICAL


def test_shap_contributions_sum_to_the_prediction() -> None:
    """SHAP's defining property. If it does not hold, it is not an explanation.

    base_value + sum(shap_values) = the model's raw margin, EXACTLY. That additivity
    is what makes SHAP an attribution with a proof behind it rather than a
    plausible-looking ranking, and it is worth asserting rather than assuming.
    """
    pytest.importorskip("shap")
    pytest.importorskip("xgboost")

    from xgboost import XGBClassifier
    import shap

    rng = np.random.RandomState(2)
    X = pd.DataFrame(rng.uniform(0, 10, (200, 6)),
                     columns=[f"f{i}" for i in range(6)])
    y = ((X["f0"] > 7) | (X["f3"] > 8)).astype(int)

    m = XGBClassifier(n_estimators=25, max_depth=3, random_state=0, verbosity=0)
    m.fit(X, y)

    explainer = shap.TreeExplainer(m)
    sv = explainer.shap_values(X)
    margins = m.predict(X, output_margin=True)

    reconstructed = explainer.expected_value + sv.sum(axis=1)
    assert np.allclose(reconstructed, margins, atol=1e-3), (
        "SHAP values do not sum to the model's output. The explanation does not "
        "reconstruct the prediction, which means it is not an explanation."
    )