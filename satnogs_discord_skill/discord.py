"""Discord webhook posting utilities."""

from __future__ import annotations

import json
import sys
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class DiscordWebhookError(RuntimeError):
    """Raised when posting to Discord fails."""


class DiscordWebhook:
    def __init__(self, webhook_url: Optional[str], *, dry_run: bool = False, timeout: int = 30) -> None:
        self.webhook_url = webhook_url
        self.dry_run = dry_run
        self.timeout = timeout

    def send(self, payload: dict[str, Any]) -> None:
        if self.dry_run:
            print(json.dumps(payload, indent=2, sort_keys=True, default=str))
            return
        if not self.webhook_url:
            raise DiscordWebhookError("No Discord webhook URL configured")
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            self.webhook_url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "SATNOGS-open-claw-skill/0.1",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                # Discord returns 204 No Content for successful webhook posts.
                if response.status not in (200, 204):
                    raise DiscordWebhookError(f"Discord webhook returned HTTP {response.status}")
        except HTTPError as exc:
            body_text = ""
            try:
                body_text = exc.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                body_text = ""
            raise DiscordWebhookError(f"Discord webhook HTTP {exc.code}: {body_text}") from exc
        except (URLError, TimeoutError) as exc:
            raise DiscordWebhookError(f"Discord webhook request failed: {exc}") from exc


def print_error(message: str) -> None:
    print(message, file=sys.stderr)
