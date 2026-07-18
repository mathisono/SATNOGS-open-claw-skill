"""Datetime helpers for SatNOGS API values and Discord display."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def parse_datetime(value: object) -> datetime | None:
    """Parse SatNOGS/ISO datetime strings and return timezone-aware UTC datetimes."""

    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            # Some SatNOGS clients format query params without timezone seconds.
            dt = datetime.strptime(text.split(".")[0], "%Y-%m-%dT%H:%M:%S")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def api_datetime(dt: datetime) -> str:
    """Format a datetime for SatNOGS Network API filters."""

    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def get_zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def display_datetime(dt: datetime | None, tz_name: str) -> str:
    if dt is None:
        return "unknown"
    zone = get_zone(tz_name)
    local = dt.astimezone(zone)
    return local.strftime("%Y-%m-%d %H:%M:%S %Z")


def duration_text(start: datetime | None, end: datetime | None) -> str:
    if not start or not end:
        return "unknown"
    seconds = max(0, int((end - start).total_seconds()))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"
