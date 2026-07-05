import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from satnogs_discord_skill.state import State


class StateTests(unittest.TestCase):
    def test_record_announcement_and_completion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            state = State.load(path)
            state.record_announcement(
                {
                    "id": 123,
                    "start": "2026-07-05T12:00:00Z",
                    "end": "2026-07-05T12:10:00Z",
                    "ground_station": 99,
                    "status": "future",
                }
            )
            self.assertTrue(state.has_announced(123))
            due = state.pending_completion_ids(now=datetime(2026, 7, 5, 12, 20, tzinfo=timezone.utc), grace_minutes=5)
            self.assertEqual(due, ["123"])
            state.record_completion({"id": 123, "status": "good"})
            self.assertEqual(state.summary()["completed"], 1)
            state.save()
            loaded = State.load(path)
            self.assertTrue(loaded.has_announced("123"))
            self.assertEqual(loaded.summary()["completed"], 1)

    def test_load_invalid_state_starts_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            path.write_text("not json", encoding="utf-8")
            state = State.load(path)
            self.assertEqual(state.summary()["total"], 0)


if __name__ == "__main__":
    unittest.main()
