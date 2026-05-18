#!/usr/bin/env python3
from __future__ import annotations

from satnogs_984_common import (
    STATION_ID,
    chunk_text,
    discord_post,
    fetch_observations_for_day,
    format_obs_line,
    is_completed,
    is_scheduled,
    load_state,
    save_state,
    today_local,
)


def main() -> int:
    today = today_local()
    obs = fetch_observations_for_day(today, STATION_ID, status="unknown")
    obs.extend(fetch_observations_for_day(today, STATION_ID, status="future"))
    state = load_state()

    if state.get("date") != today.isoformat():
        state.update({"date": today.isoformat(), "scheduled_ids": [], "reported_ids": []})

    scheduled_ids = set(state.get("scheduled_ids", []))
    reported_ids = set(state.get("reported_ids", []))

    for o in obs:
        if is_scheduled(o):
            scheduled_ids.add(o["id"])

    completed = [o for o in obs if is_completed(o) and o["id"] in scheduled_ids and o["id"] not in reported_ids]
    completed.sort(key=lambda o: o["start"])

    if not completed:
        print("No new completed passes.")
        state["scheduled_ids"] = sorted(scheduled_ids)
        state["reported_ids"] = sorted(reported_ids)
        save_state(state)
        return 0

    lines = [f"**SatNOGS 984 completed passes for {today.isoformat()}**"]
    for o in completed:
        lines.append(f"- {format_obs_line(o)}")
        reported_ids.add(o["id"])

    state["scheduled_ids"] = sorted(scheduled_ids)
    state["reported_ids"] = sorted(reported_ids)
    save_state(state)

    for part in chunk_text("\n".join(lines)):
        discord_post(part)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
