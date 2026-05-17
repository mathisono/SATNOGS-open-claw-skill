#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

UA = "kj6dzb open claw weather (contact: none)"
NOAA_URL = "https://api.weather.gov/alerts/active?area=CA"
DISCORD_API = "https://discord.com/api/v10/channels/{channel_id}/messages"
DEFAULT_CHANNEL_ID = "1494094633142194176"
STATE_FILE = Path(".openclaw/weather_alerts_state.json")

REGIONS = {
    "Bay Area": [
        "San Francisco", "San Mateo", "Santa Clara", "Alameda", "Contra Costa",
        "Marin", "Napa", "Sonoma", "Solano", "Santa Cruz", "Monterey",
        "East Bay", "North Bay", "Peninsula", "South Bay", "Coastal North Bay",
        "San Francisco Peninsula Coast", "East Bay Hills", "Santa Cruz Mountains",
    ],
    "San Joaquin Valley": [
        "San Joaquin", "Stanislaus", "Merced", "Madera", "Fresno",
        "Kings", "Tulare", "Kern", "West Side", "Delta", "San Joaquin Valley",
        "Central Valley", "San Joaquin Delta",
    ],
    "Sierra Nevada": [
        "Placer", "El Dorado", "Amador", "Calaveras", "Tuolumne",
        "Mariposa", "Mono", "Inyo", "Nevada", "Sierra", "Plumas",
        "Lassen", "Tahoe", "Yosemite", "Foothills", "Sierra Nevada",
        "County Mountains", "High Sierra",
    ],
}


def fetch_alerts():
    req = Request(NOAA_URL, headers={"User-Agent": UA, "Accept": "application/geo+json"})
    with urlopen(req, timeout=30) as resp:
        return json.load(resp).get("features", [])


def region_hits(area_desc):
    text = (area_desc or "").lower()
    hits = []
    for region, keywords in REGIONS.items():
        if any(k.lower() in text for k in keywords):
            hits.append(region)
    return hits


def fmt_alert(p):
    ends = p.get("ends", "")
    if ends:
        dt = datetime.fromisoformat(ends.replace("Z", "+00:00"))
        end_txt = dt.strftime("%b %-d %I:%M %p").replace(" 0", " ")
    else:
        end_txt = ""
    area = (p.get("areaDesc") or "").split(";")[0][:60]
    return f"- {p.get('event', 'Alert')} | {area}" + (f" | ends {end_txt}" if end_txt else "")


def build_message(groups):
    parts = ["**NOAA Active Weather Alerts**"]
    for region in REGIONS:
        items = groups.get(region, [])
        parts.append(f"\n__{region} ({len(items)})__")
        if not items:
            parts.append("- None")
            continue
        for item in items:
            parts.append(fmt_alert(item))
    return "\n".join(parts)


def chunk(text, limit=1800):
    chunks, buf = [], []
    size = 0
    for line in text.splitlines():
        add = len(line) + 1
        if buf and size + add > limit:
            chunks.append("\n".join(buf))
            buf, size = [line], add
        else:
            buf.append(line)
            size += add
    if buf:
        chunks.append("\n".join(buf))
    return chunks


def post_discord(token, channel_id, content):
    payload = json.dumps({"content": content}).encode()
    req = Request(
        DISCORD_API.format(channel_id=quote(channel_id)),
        data=payload,
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        return resp.status


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def main():
    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    channel_id = os.environ.get("DISCORD_CHANNEL_ID", DEFAULT_CHANNEL_ID).strip()
    alerts = fetch_alerts()

    grouped = {name: [] for name in REGIONS}
    seen = {name: set() for name in REGIONS}
    for alert in alerts:
        p = alert.get("properties", {})
        hits = region_hits(p.get("areaDesc", ""))
        for region in hits:
            key = (p.get("event"), p.get("headline"), p.get("areaDesc"))
            if key in seen[region]:
                continue
            seen[region].add(key)
            grouped[region].append(p)

    message = build_message(grouped)
    digest = hashlib.sha256(message.encode()).hexdigest()
    state = load_state()
    if state.get("digest") == digest:
        print("No changes; skipping Discord post.")
        return 0

    if not token:
        print(message)
        save_state({"digest": digest})
        return 0

    for part in chunk(message):
        post_discord(token, channel_id, part)

    save_state({"digest": digest})
    print("Posted weather alert summary to Discord.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
