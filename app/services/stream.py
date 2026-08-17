"""Live activity monitoring.

Replays the raw CERT event logs in chronological order as a near-real-time
feed. Each event is annotated with the risk verdict the engine computed for
that user-day, so the monitoring page shows activity *and* its threat context.
"""

from __future__ import annotations

import itertools
import threading
from collections import deque
from datetime import datetime, timezone

import pandas as pd

from config import Config

# How many events to sample from each raw source for the replay buffer.
#
# This is a pacing knob, not just a memory one. The buffer is replayed in
# chronological order, so the sample size sets how much corpus time each
# emitted event represents: ~3k events over a 160-day corpus means roughly one
# calendar day every 9 seconds of wall time, and a full pass in ~25 minutes.
# A much larger sample would leave an analyst stuck in the first week.
SAMPLE_PER_SOURCE = 600
# Rows read at a time while sampling. The sample must span the whole file:
# raw CERT logs are chronological, so reading only the head would pin the
# replay to the first few days and never surface a high-risk user-day.
SAMPLE_CHUNK = 200_000

SOURCE_SPECS = {
    "logon": {"cols": ["date", "user", "pc", "activity"], "describe": "activity"},
    "device": {"cols": ["date", "user", "pc", "activity"], "describe": "activity"},
    "file": {"cols": ["date", "user", "pc", "filename"], "describe": "filename"},
    "email": {"cols": ["date", "user", "pc", "to"], "describe": "to"},
    "http": {"cols": ["date", "user", "pc", "url"], "describe": "url"},
}


class ActivityStreamer:
    """Thread-safe cyclic replay of sampled raw activity."""

    def __init__(self, raw_dir=None, buffer_size: int | None = None):
        self.raw_dir = raw_dir or Config.RAW_DIR
        self.recent = deque(maxlen=buffer_size or Config.STREAM_BUFFER_SIZE)
        self._lock = threading.Lock()
        self._events: list[dict] = []
        self._cycle = None
        self._seq = 0
        self._loaded = False

    # -- loading ---------------------------------------------------------
    def _sample_source(self, path, cols) -> pd.DataFrame | None:
        """Draw a time-spanning sample without holding the whole file."""
        parts = []
        try:
            reader = pd.read_csv(
                path, usecols=cols, parse_dates=["date"], chunksize=SAMPLE_CHUNK
            )
        except ValueError:
            return None

        # Take up to SAMPLE_PER_SOURCE from every chunk, then thin the union.
        # Sampling per chunk keeps peak memory flat; thinning afterwards keeps
        # the result uniform across the whole time range.
        for chunk in reader:
            take = min(SAMPLE_PER_SOURCE, len(chunk))
            parts.append(chunk.sample(take, random_state=7) if take < len(chunk) else chunk)

        if not parts:
            return None
        df = pd.concat(parts, ignore_index=True)
        if len(df) > SAMPLE_PER_SOURCE:
            df = df.sample(SAMPLE_PER_SOURCE, random_state=7)
        return df

    def load(self):
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return
            frames = []
            for source, spec in SOURCE_SPECS.items():
                path = self.raw_dir / f"{source}.csv"
                if not path.exists():
                    continue
                df = self._sample_source(path, spec["cols"])
                if df is None or df.empty:
                    continue
                df["source"] = source
                df["detail"] = df[spec["describe"]].astype(str)
                frames.append(df[["date", "user", "pc", "source", "detail"]])

            if not frames:
                self._events, self._loaded = [], True
                return

            allev = pd.concat(frames, ignore_index=True).sort_values("date")
            self._events = [
                {
                    "timestamp": row.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "day": row.date.strftime("%Y-%m-%d"),
                    "hour": int(row.date.hour),
                    "user": row.user,
                    "pc": row.pc,
                    "source": row.source,
                    "detail": row.detail[:80],
                    "off_hours": bool(row.date.hour < 7 or row.date.hour >= 18),
                }
                for row in allev.itertuples(index=False)
            ]
            self._cycle = itertools.cycle(self._events)
            self._loaded = True

    # -- emission --------------------------------------------------------
    def next_batch(self, size: int = 3) -> list[dict]:
        self.load()
        if not self._events:
            return []
        with self._lock:
            batch = [dict(next(self._cycle)) for _ in range(size)]
            for event in batch:
                self._seq += 1
                event["seq"] = self._seq
                event["emitted_at"] = datetime.now(timezone.utc).strftime("%H:%M:%S")
            self._annotate(batch)
            self.recent.extend(batch)
            return batch

    def _annotate(self, batch: list[dict]):
        """Attach the engine's risk verdict for each event's user-day."""
        from app.ml import engine as eng  # local import avoids a cycle

        try:
            engine = eng.get_engine()
        except eng.ModelNotTrained:
            for event in batch:
                event.update(risk_score=None, severity="UNKNOWN")
            return

        for event in batch:
            row = engine.day_row(event["user"], event["day"])
            if row is None:
                row = engine.worst_day(event["user"])
            if row is None:
                event.update(risk_score=None, severity="UNKNOWN")
            else:
                event["risk_score"] = round(float(row["risk_score"]), 1)
                event["severity"] = row["severity"]

    def snapshot(self, limit: int = 50) -> list[dict]:
        with self._lock:
            return list(self.recent)[-limit:][::-1]


_streamer: ActivityStreamer | None = None


def get_streamer() -> ActivityStreamer:
    global _streamer
    if _streamer is None:
        _streamer = ActivityStreamer()
    return _streamer
