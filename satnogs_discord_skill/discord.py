"""OpenClaw Discord posting utilities.

The GOES Satellite GIF skill posts to Discord through OpenClaw's message CLI:

    openclaw message send --channel discord --target channel:<id> --message "..."

This module uses the same mechanism instead of talking directly to a Discord
webhook.
"""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from typing import Optional


class OpenClawDiscordError(RuntimeError):
    """Raised when OpenClaw cannot send a Discord message."""


class OpenClawDiscord:
    def __init__(
        self,
        target: Optional[str],
        *,
        channel: str = "discord",
        command: str = "openclaw",
        dry_run: bool = False,
        timeout: int = 60,
    ) -> None:
        self.target = target
        self.channel = channel
        self.command = command
        self.dry_run = dry_run
        self.timeout = timeout

    def _command_args(self, message: str, media: str | None = None, presentation: dict | None = None) -> list[str]:
        if not self.target:
            raise OpenClawDiscordError("No OpenClaw Discord target configured")
        args = shlex.split(self.command) + [
            "message",
            "send",
            "--channel",
            self.channel,
            "--target",
            self.target,
            "--message",
            message,
        ]
        if media:
            args.extend(["--media", media])
        if presentation:
            args.extend(["--presentation", json.dumps(presentation, separators=(",", ":"))])
        return args

    def send_message(self, message: str, media: str | None = None, presentation: dict | None = None) -> None:
        args = self._command_args(message, media, presentation)
        if self.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "command": shlex.join(args),
                        "message": message,
                        "media": media,
                        "presentation": presentation,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise OpenClawDiscordError(f"OpenClaw command not found: {self.command}") from exc
        except subprocess.TimeoutExpired as exc:
            raise OpenClawDiscordError("OpenClaw Discord send timed out") from exc

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            details = stderr or stdout or f"exit code {result.returncode}"
            raise OpenClawDiscordError(f"OpenClaw Discord send failed: {details}")


def print_error(message: str) -> None:
    print(message, file=sys.stderr)


# Compatibility names for code that imported the initial webhook implementation.
DiscordWebhookError = OpenClawDiscordError
