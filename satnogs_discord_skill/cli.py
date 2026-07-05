"""Command line interface for the SatNOGS Discord monitor."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from .config import Config, ConfigError, load_config
from .discord import DiscordWebhook, DiscordWebhookError, print_error
from .messages import build_completion_embed, build_upcoming_embed, webhook_payload
from .satnogs import SatnogsApiError, SatnogsClient
from .state import State


class Monitor:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = SatnogsClient(config.api_base_url, token=config.api_token)
        self.discord = DiscordWebhook(config.discord_webhook_url, dry_run=config.dry_run)
        self.state = State.load(config.state_file)

    def _send_embed(self, embed: dict[str, Any], *, content: str | None = None) -> None:
        payload = webhook_payload(
            embed=embed,
            username=self.config.discord_username,
            avatar_url=self.config.discord_avatar_url,
            content=content,
        )
        self.discord.send(payload)

    def announce_upcoming(self) -> int:
        now = datetime.now(timezone.utc)
        end_before = now + timedelta(hours=self.config.lookahead_hours)
        observations = self.client.list_future_observations(
            station_id=self.config.station_id,
            start=now,
            end_before=end_before,
            max_results=self.config.max_observations,
        )
        posted = 0
        for obs in observations:
            obs_id = obs.get("id")
            if obs_id is None or self.state.has_announced(obs_id):
                continue
            embed = build_upcoming_embed(obs, api_base_url=self.config.api_base_url, tz_name=self.config.timezone)
            self._send_embed(embed)
            self.state.record_announcement(obs)
            posted += 1
        self.state.save()
        return posted

    def list_upcoming(self) -> int:
        now = datetime.now(timezone.utc)
        end_before = now + timedelta(hours=self.config.lookahead_hours)
        observations = self.client.list_future_observations(
            station_id=self.config.station_id,
            start=now,
            end_before=end_before,
            max_results=self.config.max_observations,
        )
        for obs in observations:
            embed = build_upcoming_embed(obs, api_base_url=self.config.api_base_url, tz_name=self.config.timezone)
            self._send_embed(embed)
        return len(observations)

    def check_completed(self) -> int:
        now = datetime.now(timezone.utc)
        due_ids = self.state.pending_completion_ids(now=now, grace_minutes=self.config.completion_grace_minutes)
        posted = 0
        for obs_id in due_ids:
            obs = self.client.get_observation(obs_id)
            if str(obs.get("status") or "").lower() == "future":
                # SatNOGS has not finalized this observation yet; try again on the next run.
                continue
            embed = build_completion_embed(obs, api_base_url=self.config.api_base_url, tz_name=self.config.timezone)
            self._send_embed(embed)
            self.state.record_completion(obs)
            posted += 1
        self.state.prune()
        self.state.save()
        return posted

    def post_test(self) -> None:
        embed = {
            "title": "SatNOGS Discord monitor test",
            "description": "Webhook delivery is configured correctly.",
            "color": 0x2B90D9,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._send_embed(embed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Post SatNOGS ground-station pass notifications to Discord.")
    parser.add_argument("command", choices=["once", "announce-upcoming", "check-completed", "list-upcoming", "show-state", "post-test"])
    parser.add_argument("--station-id", type=int, help="SatNOGS ground station ID")
    parser.add_argument("--discord-webhook-url", help="Discord channel webhook URL")
    parser.add_argument("--api-base-url", help="SatNOGS Network base URL")
    parser.add_argument("--api-token", help="Optional SatNOGS Network API token")
    parser.add_argument("--state-file", help="Path to local JSON state file")
    parser.add_argument("--lookahead-hours", type=int, help="Future observation window to announce")
    parser.add_argument("--completion-grace-minutes", type=int, help="Minutes after observation end before checking completion")
    parser.add_argument("--timezone", help="Display timezone, e.g. UTC or America/Los_Angeles")
    parser.add_argument("--max-observations", type=int, help="Maximum observations to fetch per run")
    parser.add_argument("--discord-username", help="Optional webhook display username")
    parser.add_argument("--discord-avatar-url", help="Optional webhook avatar URL")
    parser.add_argument("--dry-run", action="store_true", help="Print webhook payloads instead of posting to Discord")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "show-state":
            config = load_config(args, require_webhook=False, require_station=False)
            state = State.load(config.state_file)
            print(json.dumps(state.summary(), indent=2, sort_keys=True))
            return 0

        config = load_config(args, require_webhook=args.command != "list-upcoming", require_station=True)
        monitor = Monitor(config)
        if args.command == "once":
            announced = monitor.announce_upcoming()
            completed = monitor.check_completed()
            print(f"announced={announced} completed={completed}")
        elif args.command == "announce-upcoming":
            announced = monitor.announce_upcoming()
            print(f"announced={announced}")
        elif args.command == "check-completed":
            completed = monitor.check_completed()
            print(f"completed={completed}")
        elif args.command == "list-upcoming":
            listed = monitor.list_upcoming()
            print(f"listed={listed}")
        elif args.command == "post-test":
            monitor.post_test()
            print("test_posted=1")
        else:
            parser.error(f"unknown command {args.command}")
        return 0
    except (ConfigError, SatnogsApiError, DiscordWebhookError) as exc:
        print_error(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
