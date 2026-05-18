#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
from datetime import datetime, date, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_ROOT = "https://network.satnogs.org/api/observations/"
STATION_ID = 984
TZ_NAME = os.environ.get("SATNOGS_TZ", "America/Los_Angeles")
STATE_FILE = Path(os.environ.get("SATNOGS_STATE_FILE", ".openclaw/satnogs_984_state.json"))
DISCORD_CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "1494094633142194176")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
UA = "kj6dzb open claw satnogs reporter (contact: none)"


def _tzinfo():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(TZ_NAME)
    except Exception:
        return timezone.utc


LOCAL_TZ = _tzinfo()


def today_local() -> date:
    return datetime.now(LOCAL_TZ).date()


def iso_to_local_date(iso_ts: str) -> date:
    return datetime.fromisoformat(iso_ts.replace("Z", "+00:00")).astimezone(LOCAL_TZ).date()


def iso_to_local_time(iso_ts: str) -> str:
    return datetime.fromisoformat(iso_ts.replace("Z", "+00:00")).astimezone(LOCAL_TZ).strftime("%H:%M")


def fmt_freq(hz) -> str:
    try:
        return f"{int(hz)/1_000_000:.3f} MHz"
    except Exception:
        return ""


def fetch_all_observations(station_id: int = STATION_ID):
    url = f"{API_ROOT}?ground_station={station_id}"
    out = []
    while url:
        req = Request(url, headers={"Accept": "application/json", "User-Agent": UA})
        with urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
            out.extend(payload)
            link = resp.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                start = part.find("<")
                end = part.find(">")
                if start != -1 and end != -1:
                    next_url = part[start + 1:end]
                    next_url = next_url.replace("[", "").replace("]", "")
                break
        url = next_url
    return out


def _open_json(url: str, retries: int = 3):
    last = None
    for attempt in range(retries):
        try:
            req = Request(url, headers={"Accept": "application/json", "User-Agent": UA})
            with urlopen(req, timeout=30) as resp:
                return json.load(resp), resp.headers.get("Link", "")
        except HTTPError as e:
            last = e
            if e.code != 429 or attempt == retries - 1:
                raise
            retry_after = e.headers.get("Retry-After") if e.headers else None
            sleep_for = float(retry_after) if retry_after and retry_after.isdigit() else (2 ** attempt)
            time.sleep(sleep_for)
    raise last


def fetch_observations_for_day(day: date, station_id: int = STATION_ID, **query):
    params = {"ground_station": station_id, **query}
    url = f"{API_ROOT}?{urlencode(params)}"
    out = []
    while url:
        page, link = _open_json(url)
        out.extend([o for o in page if iso_to_local_date(o["start"]) == day])
        if page and iso_to_local_date(page[-1]["start"]) < day:
            break
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                start = part.find("<")
                end = part.find(">")
                if start != -1 and end != -1:
                    next_url = part[start + 1:end].replace("[", "").replace("]", "")
                break
        url = next_url
    return out


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"date": None, "scheduled_ids": [], "reported_ids": []}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def discord_post(content: str) -> None:
    if not DISCORD_BOT_TOKEN:
        print(content)
        return
    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
    body = json.dumps({"content": content}).encode()
    req = Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        resp.read()


def chunk_text(text: str, limit: int = 1800):
    chunks = []
    buf = []
    size = 0
    for line in text.splitlines():
        n = len(line) + 1
        if buf and size + n > limit:
            chunks.append("\n".join(buf))
            buf = [line]
            size = n
        else:
            buf.append(line)
            size += n
    if buf:
        chunks.append("\n".join(buf))
    return chunks


def obs_key(obs: dict) -> int:
    return int(obs["id"])


def is_today(obs: dict, day: date) -> bool:
    return iso_to_local_date(obs["start"]) == day


def is_scheduled(obs: dict) -> bool:
    return obs.get("status") == "future"


def is_completed(obs: dict) -> bool:
    return bool(obs.get("payload") or obs.get("waterfall")) and obs.get("status") != "future"


def format_obs_line(obs: dict) -> str:
    parts = [f"{iso_to_local_time(obs['start'])}", f"ID {obs['id']}", obs.get("sat_id", "")]
    freq = fmt_freq(obs.get("observation_frequency"))
    if freq:
        parts.append(freq)
    if obs.get("transmitter_description"):
        parts.append(obs["transmitter_description"])
    return " | ".join([p for p in parts if p])
