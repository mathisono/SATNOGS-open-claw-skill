#!/usr/bin/env python3
"""Render a compact SatNOGS post-pass data report.

Usage:
  python3 scripts/satnogs_post_report.py \
    --id 13884987 --ground-station 984 --sat-id UBGG-0313-1046-0311-8192 \
    --start 2026-04-23T10:19:12Z --end 2026-04-23T10:27:21Z \
    --observation-frequency 145850000 \
    --payload https://...ogg --waterfall https://...png --status unknown
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def fmt_freq(hz: str | int | None) -> str:
    if hz in (None, ""):
        return ""
    try:
        return f"{int(hz)/1_000_000:.3f} MHz"
    except (TypeError, ValueError):
        return str(hz)


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text())


def build_post(d: dict) -> str:
    lines = [f"SatNOGS post-pass data report for station {d.get('ground_station', '')}", ""]
    lines.append(f"- ID: {d.get('id', '')}")
    lines.append(f"  ground_station: {d.get('ground_station', '')}")
    lines.append(f"  sat_id: {d.get('sat_id', '')}")
    lines.append(f"  start: {d.get('start', '')}")
    lines.append(f"  end: {d.get('end', '')}")
    lines.append(f"  observation_frequency: {d.get('observation_frequency', '')}" + (f" ({fmt_freq(d.get('observation_frequency'))})" if d.get('observation_frequency') else ""))
    if d.get("payload"):
        lines.append(f"  payload: {d['payload']}")
    if d.get("waterfall"):
        lines.append(f"  waterfall: {d['waterfall']}")
    lines.append(f"  status: {d.get('status', 'unknown')}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", help="Load fields from a JSON file")
    p.add_argument("--id")
    p.add_argument("--ground-station")
    p.add_argument("--sat-id")
    p.add_argument("--start")
    p.add_argument("--end")
    p.add_argument("--observation-frequency")
    p.add_argument("--payload")
    p.add_argument("--waterfall")
    p.add_argument("--status", default="unknown")
    args = p.parse_args()

    data = load_json(args.json) if args.json else vars(args)
    data.pop("json", None)
    print(build_post(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
