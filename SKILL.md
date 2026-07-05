---
name: satnogs-discord-pass-monitor
description: Announce upcoming SatNOGS Network observations for a ground station to Discord and post completion summaries after each pass finishes. Use for SatNOGS station pass monitoring, Discord webhook notifications, and cron/systemd automation.
---

# SatNOGS Discord Pass Monitor Skill

Use this skill when the user wants to monitor a SatNOGS ground station, announce upcoming satellite passes/observations, or publish post-pass summaries to a Discord channel.

## What this skill does

- Reads scheduled observations from the SatNOGS Network API for one ground station ID.
- Posts each newly discovered future observation to a Discord webhook.
- Stores local state so the same pass is not announced repeatedly.
- Checks previously announced observations after their end time and posts a completion summary when SatNOGS reports a final status.
- Supports `cron` or `systemd` timer execution through `python -m satnogs_discord_skill once`.

## Required configuration

Set these environment variables before running the skill:

```bash
export SATNOGS_STATION_ID="1234"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

The Discord webhook must be created in the target channel. If the desired channel is named `satalite-data` or `satellite-data`, create the webhook in that channel; this skill does not need a Discord bot token or channel ID.

Optional environment variables:

```bash
export SATNOGS_LOOKAHEAD_HOURS="24"             # future window to announce
export SATNOGS_COMPLETION_GRACE_MINUTES="5"     # wait after end before checking status
export SATNOGS_TIMEZONE="UTC"                   # display timezone, e.g. America/Los_Angeles
export SATNOGS_STATE_FILE=".satnogs_state.json" # duplicate-prevention state
export SATNOGS_API_TOKEN=""                     # optional SatNOGS Network token for higher rate limits
export SATNOGS_API_BASE_URL="https://network.satnogs.org"
```

Never print, commit, or paste `DISCORD_WEBHOOK_URL` or `SATNOGS_API_TOKEN` into public logs or issues.

## Standard operating workflow

1. Install or run from the repository root.
2. Export the required environment variables.
3. Run a dry run first:

   ```bash
   python -m satnogs_discord_skill once --dry-run
   ```

4. Run the live command:

   ```bash
   python -m satnogs_discord_skill once
   ```

5. Add the command to cron or a systemd timer. A 5-10 minute interval is usually enough for both new pass discovery and post-pass checks.

## Commands

- `python -m satnogs_discord_skill once` announces new upcoming observations and checks completed observations.
- `python -m satnogs_discord_skill announce-upcoming` only posts newly discovered future observations.
- `python -m satnogs_discord_skill check-completed` only checks previously announced observations whose end time has passed.
- `python -m satnogs_discord_skill list-upcoming --dry-run` prints upcoming observation embeds without posting.
- `python -m satnogs_discord_skill show-state` prints the local state file summary.
- `python -m satnogs_discord_skill post-test` sends a small webhook test message.

## Implementation notes

SatNOGS has multiple public services. This skill uses the SatNOGS Network observation endpoints for passes/observations. The SatNOGS DB API is useful for satellite and transmitter metadata, but scheduled observations are read from the Network API.

The code is intentionally dependency-free and uses Python standard library HTTP clients so it is easy to run from small cron hosts.
