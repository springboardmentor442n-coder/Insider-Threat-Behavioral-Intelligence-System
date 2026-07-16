"""The detector ensemble: all four models train, evaluate, and get compared.

This is a STRUCTURAL test - it asserts the pipeline produces every model's
metrics and the two comparison verdicts, not that the numbers hit any particular
value (real metrics come from the full dataset, not the CI fixture). It runs only
when feature data exists; without it, it skips like the other pipeline tests.

Why it earns its place: adding LOF and LightGBM touched run_detection, and a
silent failure there (a model that stops training, a comparison key that
disappears) would not show up anywhere else until someone read the training
output by hand.
"""
from __future__ import annotations

import pytest

from backend.app.database import SessionLocal
from backend.app.features_models import DailyFeatures


def _has_features() -> bool:
    with SessionLocal() as db:
        return db.query(DailyFeatures).first() is not None


@pytest.fixture(scope="module")
def detection_results():
    if not _has_features():
        pytest.skip("no features built - run the pipeline")
    pytest.importorskip("xgboost")
    pytest.importorskip("lightgbm")
    from backend.app.detection import run_detection
    with SessionLocal() as db:
        return run_detection(db, save_models_to_disk=False)


def test_all_four_detectors_are_evaluated(detection_results):
    r = detection_results
    for model in ("isolation_forest", "local_outlier_factor", "xgboost", "lightgbm"):
        assert model in r, f"{model} missing from results"
        # each carries the core metrics
        assert {"recall", "precision", "f1"} <= set(r[model])


def test_every_metric_is_in_range(detection_results):
    r = detection_results
    for model in ("isolation_forest", "local_outlier_factor", "xgboost", "lightgbm"):
        m = r[model]
        assert 0.0 <= m["recall"] <= 1.0
        assert 0.0 <= m["precision"] <= 1.0
        assert 0.0 <= m["false_positive_rate"] <= 1.0


def test_supervised_comparison_picks_a_winner(detection_results):
    r = detection_results
    sc = r["supervised_comparison"]
    assert sc["winner"] in ("xgboost", "lightgbm")
    # the winner must be the one with the higher (or equal) PR-AUC
    if sc["winner"] == "xgboost":
        assert sc["xgboost_pr_auc"] >= sc["lightgbm_pr_auc"]
    else:
        assert sc["lightgbm_pr_auc"] > sc["xgboost_pr_auc"]


def test_lof_uses_the_same_feature_view_as_isolation_forest(detection_results):
    """LOF and Isolation Forest must be fed the SAME deviation features - that is
    what makes 'local vs global' a fair comparison rather than two models seeing
    two different problems."""
    r = detection_results
    assert r["local_outlier_factor"]["n_features"] == r["isolation_forest"]["n_features"]
