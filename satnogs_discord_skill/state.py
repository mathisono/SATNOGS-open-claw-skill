"""Persistent duplicate-prevention state for announced SatNOGS observations."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .timeutils import parse_datetime

STATE_VERSION = 1


@dataclass
class State:
    path: Path
    records: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "State":
        if not path.exists():
            return cls(path=path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # Preserve bad files for manual inspection and start fresh.
            return cls(path=path)
        records = data.get("records", {}) if isinstance(data, dict) else {}
        if not isinstance(records, dict):
            records = {}
        return cls(path=path, records=records)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": STATE_VERSION,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "records": self.records,
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)

    def has_announced(self, observation_id: int | str) -> bool:
        return str(observation_id) in self.records

    def record_announcement(self, observation: dict[str, Any]) -> None:
        obs_id = str(observation.get("id"))
        self.records[obs_id] = {
            "id": obs_id,
            "announced_at": datetime.now(timezone.utc).isoformat(),
            "start": observation.get("start"),
            "end": observation.get("end"),
            "station_id": observation.get("ground_station"),
            "norad_cat_id": observation.get("norad_cat_id"),
            "sat_id": observation.get("sat_id"),
            "last_status": observation.get("status"),
            "completion_posted_at": self.records.get(obs_id, {}).get("completion_posted_at"),
        }

    def pending_completion_ids(self, *, now: datetime, grace_minutes: int) -> list[str]:
        due: list[str] = []
        grace = timedelta(minutes=grace_minutes)
        for obs_id, record in self.records.items():
            if record.get("completion_posted_at"):
                continue
            end = parse_datetime(record.get("end"))
            if end and now >= end + grace:
                due.append(obs_id)
        return sorted(due, key=lambda item: parse_datetime(self.records[item].get("end")) or datetime.max.replace(tzinfo=timezone.utc))

    def record_completion(self, observation: dict[str, Any]) -> None:
        obs_id = str(observation.get("id"))
        record = self.records.setdefault(obs_id, {"id": obs_id})
        record.update(
            {
                "last_status": observation.get("status"),
                "vetted_status": observation.get("vetted_status"),
                "waterfall_status": observation.get("waterfall_status"),
                "completion_posted_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def prune(self, *, older_than_days: int = 14, now: datetime | None = None) -> int:
        """Remove completed records whose end time is older than the retention window."""

        now = now or datetime.now(timezone.utc)
        cutoff = now - timedelta(days=older_than_days)
        before = len(self.records)
        kept: dict[str, dict[str, Any]] = {}
        for obs_id, record in self.records.items():
            end = parse_datetime(record.get("end"))
            if record.get("completion_posted_at") and end and end < cutoff:
                continue
            kept[obs_id] = record
        self.records = kept
        return before - len(self.records)

    def summary(self) -> dict[str, int]:
        total = len(self.records)
        completed = sum(1 for record in self.records.values() if record.get("completion_posted_at"))
        return {"total": total, "pending_completion": total - completed, "completed": completed}
