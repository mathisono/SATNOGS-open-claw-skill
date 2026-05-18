#!/usr/bin/env python3
from __future__ import annotations

from satnogs_984_common import (
    STATION_ID,
    chunk_text,
    discord_post,
    fetch_observations_for_day,
    format_obs_line,
    is_scheduled,
    load_state,
    save_state,
    today_local,
)


def main() -> int:
    today = today_local()
    obs = fetch_observations_for_day(today, STATION_ID, status="future")
    scheduled = [o for o in obs if is_scheduled(o)]
    scheduled.sort(key=lambda o: o["start"])

    state = load_state()
    state.update({
        "date": today.isoformat(),
        "scheduled_ids": [o["id"] for o in scheduled],
        "reported_ids": [],
    })
    save_state(state)

    lines = [f"**SatNOGS 984 scheduled passes for {today.isoformat()}**"]
    if not scheduled:
        lines.append("- None")
    else:
        lines.extend(f"- {format_obs_line(o)}" for o in scheduled)

    for part in chunk_text("\n".join(lines)):
        discord_post(part)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
