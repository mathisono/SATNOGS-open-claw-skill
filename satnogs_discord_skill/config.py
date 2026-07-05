"""Configuration loading for the SatNOGS Discord monitor."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    station_id: int
    discord_webhook_url: Optional[str]
    api_base_url: str
    api_token: Optional[str]
    state_file: Path
    lookahead_hours: int
    completion_grace_minutes: int
    timezone: str
    max_observations: int
    dry_run: bool
    discord_username: Optional[str]
    discord_avatar_url: Optional[str]


def _get_value(cli_value: object, env_name: str, default: object = None) -> object:
    if cli_value is not None:
        return cli_value
    return os.getenv(env_name, default)


def _to_int(value: object, name: str, *, minimum: int | None = None) -> int:
    try:
        parsed = int(str(value))
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{name} must be an integer") from exc
    if minimum is not None and parsed < minimum:
        raise ConfigError(f"{name} must be >= {minimum}")
    return parsed


def _empty_to_none(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def load_config(args, *, require_webhook: bool = True, require_station: bool = True) -> Config:
    """Build a Config from argparse args and environment variables."""

    station_raw = _get_value(getattr(args, "station_id", None), "SATNOGS_STATION_ID")
    if require_station and not station_raw:
        raise ConfigError("SATNOGS_STATION_ID or --station-id is required")
    station_id = _to_int(station_raw or 0, "SATNOGS_STATION_ID", minimum=1)

    webhook = _empty_to_none(
        _get_value(getattr(args, "discord_webhook_url", None), "DISCORD_WEBHOOK_URL")
    )
    dry_run = bool(getattr(args, "dry_run", False))
    if require_webhook and not dry_run and not webhook:
        raise ConfigError("DISCORD_WEBHOOK_URL or --discord-webhook-url is required unless --dry-run is used")

    return Config(
        station_id=station_id,
        discord_webhook_url=webhook,
        api_base_url=str(_get_value(getattr(args, "api_base_url", None), "SATNOGS_API_BASE_URL", "https://network.satnogs.org")).rstrip("/"),
        api_token=_empty_to_none(_get_value(getattr(args, "api_token", None), "SATNOGS_API_TOKEN")),
        state_file=Path(str(_get_value(getattr(args, "state_file", None), "SATNOGS_STATE_FILE", ".satnogs_state.json"))).expanduser(),
        lookahead_hours=_to_int(_get_value(getattr(args, "lookahead_hours", None), "SATNOGS_LOOKAHEAD_HOURS", 24), "SATNOGS_LOOKAHEAD_HOURS", minimum=1),
        completion_grace_minutes=_to_int(_get_value(getattr(args, "completion_grace_minutes", None), "SATNOGS_COMPLETION_GRACE_MINUTES", 5), "SATNOGS_COMPLETION_GRACE_MINUTES", minimum=0),
        timezone=str(_get_value(getattr(args, "timezone", None), "SATNOGS_TIMEZONE", "UTC")),
        max_observations=_to_int(_get_value(getattr(args, "max_observations", None), "SATNOGS_MAX_OBSERVATIONS", 100), "SATNOGS_MAX_OBSERVATIONS", minimum=1),
        dry_run=dry_run,
        discord_username=_empty_to_none(_get_value(getattr(args, "discord_username", None), "DISCORD_USERNAME")),
        discord_avatar_url=_empty_to_none(_get_value(getattr(args, "discord_avatar_url", None), "DISCORD_AVATAR_URL")),
    )
