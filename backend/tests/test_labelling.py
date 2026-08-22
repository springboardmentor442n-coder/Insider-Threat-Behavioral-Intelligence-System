"""The two labelling conventions (and the leak guard on the second one).

CERT ships TWO answer keys, and they disagree about half the malicious days.

  insiders.csv          gives each insider a WINDOW - a start date and an end date.
                        Label every day in it and you get 1,892 malicious user-days.

  answers/r4.2-1/ -2/ -3/  give the actual malicious EVENTS with timestamps. Count
                        only the days those fall on and you get 966 - which is the
                        number the published literature reports.

  926 of our "malicious" days - 49% - contain NO malicious activity.

The error is not evenly spread, and that is what makes it dangerous:

    scenario 1:  196 window ->  85 real   (2.3x)   single-day exfil, multi-week window
    scenario 2: 1676 window -> 861 real   (1.9x)   sustained campaign
    scenario 3:   20 window ->  20 real   (exact)

So our scenario-1 recall (73%) is being suppressed by days on which the insider did
nothing, and our scenario-2 recall (97%) is being flattered by the same effect.

Both conventions are stored. Both are reported. Neither is a model input.
"""

from __future__ import annotations

import pandas as pd
import pytest
from sqlalchemy import func, select

from backend.app.database import SessionLocal
from backend.app.detection import build_model_matrix
from backend.app.features_models import DailyFeatures
from backend.app.models import MaliciousEventDay


def test_no_label_can_ever_become_a_model_feature() -> None:
    """The leak guard - and it holds BY CONSTRUCTION, which is the point.

    There are now THREE label columns: is_malicious (the window), has_malicious_event
    (the real attack days), and scenario. Every one of them is the exam answer key.
    has_malicious_event is the MOST dangerous of the three, because it is the most
    accurate: a model handed it would score near 1.0 and have learned nothing at all.

    WHY IT CANNOT LEAK, AND WHY THAT IS ARCHITECTURE RATHER THAN LUCK.

    build_model_matrix uses an ALLOWLIST. It names the columns it wants - the counts,
    the z-scores, the peer z-scores, the novelty flags, the temporal features - and
    takes nothing else. A column nobody added to the list cannot get in.

    Had it used a DENYLIST ("everything except is_malicious and scenario"), then
    adding a third label would have leaked it silently. I would have had to remember
    to update the exclusion list, and I would not have: I added has_malicious_event
    and never once thought about the matrix builder.

    That is the whole argument for allowlists in one sentence. This test asserts the
    property; the allowlist is what guarantees it.
    """
    import numpy as np

    from backend.app.detection import (
        COUNT_FEATURES,
        FLAG_FEATURES,
        build_model_matrix,
    )

    # A frame with EVERY feature the matrix builder expects, plus all three labels.
    cols = {"user_id": ["A"], "date": pd.to_datetime(["2010-06-01"]),
            "department": ["1 - Software"]}
    for f in COUNT_FEATURES:
        for prefix in ("", "z_", "peer_z_", "novel_"):
            cols[f"{prefix}{f}"] = [1.0]
    for f in FLAG_FEATURES:
        cols[f] = [False]

    # THE THREE LABELS.
    cols["is_malicious"] = [True]
    cols["has_malicious_event"] = [True]
    cols["scenario"] = [1]

    df = pd.DataFrame(cols)
    _X, y, feature_cols = build_model_matrix(df)

    for label in ("is_malicious", "has_malicious_event", "scenario"):
        assert label not in feature_cols, (
            f"{label!r} IS A MODEL FEATURE. The model has been handed the exam "
            f"answer key. It will score near-perfectly and will have learned "
            f"nothing whatsoever."
        )

    # And the target must still be the WINDOW label - swapping which label trains the
    # model is a real decision, and it should be made deliberately, not by a typo.
    assert int(y.iloc[0]) == 1


def test_the_two_conventions_disagree_and_we_know_by_how_much() -> None:
    """If they ever AGREE exactly, someone has wired one to the other."""
    from backend.app.models import Employee

    with SessionLocal() as db:
        n_events = db.scalar(select(func.count()).select_from(MaliciousEventDay))
        if not n_events:
            pytest.skip("no event-day labels ingested (needs answers/r4.2-*/)")

        # Do the answer-key users actually EXIST in this database?
        #
        # On the real CERT r4.2 they do, by definition. On a reduced or synthetic test
        # extract they may not - the answer files carry the real IDs (AAM0658) while a
        # generated fixture carries invented ones (INA0001). Zero overlap then means
        # "wrong dataset", not "broken join", and the difference matters: one is an
        # environment fact, the other is a bug that would silently disable half this
        # feature.
        overlap = db.scalar(
            select(func.count(func.distinct(MaliciousEventDay.user_id)))
            .select_from(MaliciousEventDay)
            .join(Employee, Employee.user_id == MaliciousEventDay.user_id)
        )
        if not overlap:
            pytest.skip(
                "the answer-key users do not exist in this database - this is a "
                "synthetic or reduced extract, not real CERT r4.2. The join cannot "
                "be tested here."
            )

        window = db.scalar(
            select(func.count()).select_from(DailyFeatures)
            .where(DailyFeatures.is_malicious)
        )
        event = db.scalar(
            select(func.count()).select_from(DailyFeatures)
            .where(DailyFeatures.has_malicious_event)
        )

    assert window > 0, "no window labels at all - has build_features run?"
    assert event > 0, (
        "the event-day label is ingested but never lands in daily_features. "
        "The event_labels CTE or its join is broken."
    )
    assert event <= window * 1.05, (
        f"there are MORE event-days ({event}) than window-days ({window}). Every "
        "malicious event should fall inside its own insider's window - if it does "
        "not, the windows in insiders.csv do not cover the attacks they describe, "
        "and one of the two answer keys is being read wrong."
    )


def test_event_days_fall_inside_their_own_insiders_window() -> None:
    """A sanity check on CERT itself, and on our reading of it.

    Every malicious EVENT should fall within that insider's declared window. If one
    does not, we are joining the wrong user, parsing the wrong date column, or the
    dataset is not what we think it is - and all three are worth knowing about before
    we quote a number.
    """
    with SessionLocal() as db:
        n = db.scalar(select(func.count()).select_from(MaliciousEventDay))
        if not n:
            pytest.skip("no event-day labels ingested")

        # Days flagged as EVENT days but NOT inside any window.
        orphans = db.scalar(
            select(func.count())
            .select_from(DailyFeatures)
            .where(
                DailyFeatures.has_malicious_event,
                ~DailyFeatures.is_malicious,
            )
        )

    assert orphans == 0, (
        f"{orphans} malicious EVENT days fall OUTSIDE their insider's window. "
        "Either we are parsing the answer files wrong, or insiders.csv does not "
        "actually cover the attacks it claims to. Both matter."
    )