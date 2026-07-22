"""Discord message builders for SatNOGS observations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .satnogs import observation_page_url
from .timeutils import display_datetime, duration_text, parse_datetime

DISCORD_FIELD_LIMIT = 1024
DISCORD_MESSAGE_LIMIT = 1900


def truncate(value: object, limit: int = DISCORD_FIELD_LIMIT) -> str:
    text = "unknown" if value is None or value == "" else str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def safe_text(value: object, limit: int = DISCORD_FIELD_LIMIT) -> str:
    """Return Discord-safe text that avoids accidental mass mentions."""

    return truncate(value, limit).replace("@", "@\u200b")


def trim_message(message: str, limit: int = DISCORD_MESSAGE_LIMIT) -> str:
    if len(message) <= limit:
        return message
    return message[: limit - 1] + "…"


def frequency_mhz(value: object) -> str:
    if value in (None, ""):
        return "unknown"
    try:
        hz = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{hz / 1_000_000:.3f} MHz"


def degrees(value: object) -> str:
    if value in (None, ""):
        return "unknown"
    try:
        return f"{float(value):.1f}°"
    except (TypeError, ValueError):
        return str(value)


def status_emoji(status: object) -> str:
    status_text = str(status or "unknown").lower()
    return {
        "future": "🛰️",
        "good": "✅",
        "bad": "❌",
        "unknown": "❔",
        "failed": "⚠️",
    }.get(status_text, "ℹ️")


def satellite_label(obs: dict[str, Any]) -> str:
    sat_id = obs.get("sat_id")
    norad = obs.get("norad_cat_id")
    if sat_id and norad:
        return f"{safe_text(sat_id)} / NORAD {safe_text(norad)}"
    if sat_id:
        return safe_text(sat_id)
    if norad:
        return f"NORAD {safe_text(norad)}"
    return "unknown satellite"


def observation_title(obs: dict[str, Any], *, prefix: str) -> str:
    obs_id = obs.get("id", "unknown")
    return f"{prefix}: {satellite_label(obs)} (Observation #{safe_text(obs_id)})"


def common_fields(obs: dict[str, Any], tz_name: str) -> list[dict[str, Any]]:
    start = parse_datetime(obs.get("start"))
    end = parse_datetime(obs.get("end"))
    return [
        {"name": "Ground station", "value": truncate(obs.get("station_name") or obs.get("ground_station")), "inline": True},
        {"name": "Start", "value": display_datetime(start, tz_name), "inline": True},
        {"name": "End", "value": display_datetime(end, tz_name), "inline": True},
        {"name": "Duration", "value": duration_text(start, end), "inline": True},
        {"name": "Mode", "value": truncate(obs.get("transmitter_mode")), "inline": True},
        {"name": "Downlink", "value": frequency_mhz(obs.get("transmitter_downlink_low") or obs.get("observation_frequency") or obs.get("center_frequency")), "inline": True},
        {"name": "Max altitude", "value": degrees(obs.get("max_altitude")), "inline": True},
        {"name": "Rise / set azimuth", "value": f"{degrees(obs.get('rise_azimuth'))} / {degrees(obs.get('set_azimuth'))}", "inline": True},
    ]


def _line(label: str, value: object) -> str:
    return f"**{label}:** {safe_text(value, 500)}"


def format_upcoming_message(obs: dict[str, Any], *, api_base_url: str, tz_name: str) -> str:
    start = parse_datetime(obs.get("start"))
    end = parse_datetime(obs.get("end"))
    obs_id = obs.get("id", "unknown")
    tx_desc = obs.get("transmitter_description") or obs.get("transmitter_uuid") or obs.get("transmitter")
    message = "\n".join(
        [
            f"🛰️ **Upcoming SatNOGS pass** — {satellite_label(obs)} (Observation #{safe_text(obs_id)})",
            _line("Station", obs.get("station_name") or obs.get("ground_station")),
            _line("Start", display_datetime(start, tz_name)),
            _line("End", display_datetime(end, tz_name)),
            _line("Duration", duration_text(start, end)),
            _line("Mode", obs.get("transmitter_mode")),
            _line("Downlink", frequency_mhz(obs.get("transmitter_downlink_low") or obs.get("observation_frequency") or obs.get("center_frequency"))),
            _line("Max altitude", degrees(obs.get("max_altitude"))),
            _line("Rise / set azimuth", f"{degrees(obs.get('rise_azimuth'))} / {degrees(obs.get('set_azimuth'))}"),
            _line("Transmitter", tx_desc),
            observation_page_url(api_base_url, obs_id),
        ]
    )
    return trim_message(message)


def demoddata_count(obs: dict[str, Any]) -> str:
    frames = obs.get("demoddata")
    if isinstance(frames, list):
        return str(len(frames))
    return "0"


def format_completion_message(obs: dict[str, Any], *, api_base_url: str, tz_name: str) -> str:
    start = parse_datetime(obs.get("start"))
    end = parse_datetime(obs.get("end"))
    obs_id = obs.get("id", "unknown")
    status = obs.get("status") or "unknown"
    pass_url = observation_page_url(api_base_url, obs_id)
    message = "\n".join(
        [
            f"{status_emoji(status)} **SatNOGS pass complete** — {satellite_label(obs)} (Observation #{safe_text(obs_id)})",
            _line("Station", obs.get("station_name") or obs.get("ground_station")),
            _line("Start", display_datetime(start, tz_name)),
            _line("End", display_datetime(end, tz_name)),
            _line("Duration", duration_text(start, end)),
            _line("Final status", status),
            _line("Vetted status", obs.get("vetted_status")),
            _line("Waterfall status", obs.get("waterfall_status")),
            _line("Demodulated frames", demoddata_count(obs)),
            f"**Pass page:** {pass_url}",
        ]
    )
    return trim_message(message)


def completion_waterfall_media(obs: dict[str, Any]) -> str | None:
    waterfall = obs.get("waterfall")
    if not waterfall:
        return None
    return str(waterfall)


def completion_pass_button(obs: dict[str, Any], *, api_base_url: str) -> dict[str, Any]:
    obs_id = obs.get("id", "unknown")
    return {
        "blocks": [
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "Open pass",
                        "url": observation_page_url(api_base_url, obs_id),
                    }
                ],
            }
        ]
    }


def build_upcoming_embed(obs: dict[str, Any], *, api_base_url: str, tz_name: str) -> dict[str, Any]:
    obs_id = obs.get("id", "unknown")
    fields = common_fields(obs, tz_name)
    tx_desc = obs.get("transmitter_description") or obs.get("transmitter_uuid") or obs.get("transmitter")
    fields.append({"name": "Transmitter", "value": truncate(tx_desc), "inline": False})
    return {
        "title": observation_title(obs, prefix="Upcoming SatNOGS pass"),
        "url": observation_page_url(api_base_url, obs_id),
        "description": "A future observation has been scheduled for this ground station.",
        "color": 0x2B90D9,
        "fields": fields,
        "footer": {"text": "SatNOGS Network pass monitor"},
        "timestamp": (parse_datetime(obs.get("start")) or datetime.utcnow()).isoformat(),
    }


def build_completion_embed(obs: dict[str, Any], *, api_base_url: str, tz_name: str) -> dict[str, Any]:
    obs_id = obs.get("id", "unknown")
    status = obs.get("status") or "unknown"
    fields = common_fields(obs, tz_name)
    fields.extend(
        [
            {"name": "Final status", "value": f"{status_emoji(status)} {truncate(status)}", "inline": True},
            {"name": "Vetted status", "value": truncate(obs.get("vetted_status")), "inline": True},
            {"name": "Waterfall status", "value": truncate(obs.get("waterfall_status")), "inline": True},
            {"name": "Demodulated frames", "value": demoddata_count(obs), "inline": True},
        ]
    )
    links: list[str] = [f"[Observation]({observation_page_url(api_base_url, obs_id)})"]
    if obs.get("waterfall"):
        links.append(f"[Waterfall]({obs['waterfall']})")
    if obs.get("archive_url"):
        links.append(f"[Archive]({obs['archive_url']})")
    if obs.get("payload"):
        links.append(f"[Payload]({obs['payload']})")
    fields.append({"name": "Links", "value": " · ".join(links), "inline": False})
    return {
        "title": observation_title(obs, prefix="SatNOGS pass complete"),
        "url": observation_page_url(api_base_url, obs_id),
        "description": f"Observation finished with status: **{truncate(status, 100)}**",
        "color": 0x2ECC71 if str(status).lower() == "good" else 0xE67E22,
        "fields": fields,
        "footer": {"text": "SatNOGS Network pass monitor"},
        "timestamp": (parse_datetime(obs.get("end")) or datetime.utcnow()).isoformat(),
    }


def webhook_payload(*, embed: dict[str, Any], username: str | None = None, avatar_url: str | None = None, content: str | None = None) -> dict[str, Any]:
    """Build the legacy Discord webhook payload.

    The current skill posts through OpenClaw's Discord connector. This helper is
    retained only for compatibility with the initial webhook implementation.
    """

    payload: dict[str, Any] = {"embeds": [embed]}
    if content:
        payload["content"] = content
    if username:
        payload["username"] = username
    if avatar_url:
        payload["avatar_url"] = avatar_url
    return payload
