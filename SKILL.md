---
name: satnogs-discord-pass-monitor
description: Announce upcoming SatNOGS Network observations for a ground station to Discord through OpenClaw's Discord connector and post completion summaries after each pass finishes. Use for SatNOGS station pass monitoring, OpenClaw Discord notifications, and cron/systemd automation.
---

# SatNOGS Discord Pass Monitor Skill

Use this skill when the user wants to monitor a SatNOGS ground station, announce upcoming satellite passes/observations, or publish post-pass summaries to a Discord channel.

## What this skill does

- Reads scheduled observations from the SatNOGS Network API for one ground station ID.
- Posts each newly discovered future observation through the same OpenClaw Discord message flow used by `goes-satellite-gif`.
- Stores local state so the same pass is not announced repeatedly.
- Checks previously announced observations after their end time and posts a completion summary when SatNOGS reports a final status.
- Supports `cron` or `systemd` timer execution through `python -m satnogs_discord_skill once`.

## Required configuration

Set these environment variables before running the skill:

```bash
export SATNOGS_STATION_ID="984"
export SATNOGS_API_TOKEN="<your SatNOGS API token>"
export OPENCLAW_DISCORD_TARGET="channel:1494094633142194176"
```

`OPENCLAW_DISCORD_TARGET` should match the OpenClaw Discord target format used by the GOES skill. You can also set `DISCORD_CHANNEL_ID="1494094633142194176"` instead, and the skill will convert it to `channel:1494094633142194176`.

Optional environment variables:

```bash
export SATNOGS_LOOKAHEAD_HOURS="24"             # future window to announce
export SATNOGS_COMPLETION_GRACE_MINUTES="5"     # wait after end before checking status
export SATNOGS_TIMEZONE="America/Los_Angeles"   # display timezone
export SATNOGS_STATE_FILE=".satnogs_state.json" # duplicate-prevention state
export SATNOGS_API_BASE_URL="https://network.satnogs.org"
export OPENCLAW_DISCORD_CHANNEL="discord"       # OpenClaw connector name
export OPENCLAW_COMMAND="openclaw"              # OpenClaw CLI executable
```

Never print, commit, or paste `SATNOGS_API_TOKEN` into public logs or issues.

## Discord posting model

This skill does not require a Discord webhook. It shells out to OpenClaw exactly like the GOES Satellite GIF skill:

```bash
openclaw message send \
  --channel discord \
  --target channel:1494094633142194176 \
  --message "SatNOGS pass update..."
```

That means OpenClaw's Discord integration must already be configured and working for the Linux user that runs the cron job.

## Standard operating workflow

1. Install or run from the repository root.
2. Export the required environment variables.
3. Verify OpenClaw Discord can see the configured channel:

   ```bash
   openclaw channels status --deep
   ```

4. Run a dry run first:

   ```bash
   python -m satnogs_discord_skill once --dry-run
   ```

5. Run the live command:

   ```bash
   python -m satnogs_discord_skill once
   ```

6. Add the command to cron or a systemd timer. A 5-10 minute interval is usually enough for both new pass discovery and post-pass checks.

## Commands

- `python -m satnogs_discord_skill once` announces new upcoming observations and checks completed observations.
- `python -m satnogs_discord_skill announce-upcoming` only posts newly discovered future observations.
- `python -m satnogs_discord_skill check-completed` only checks previously announced observations whose end time has passed.
- `python -m satnogs_discord_skill list-upcoming` prints upcoming observation messages without posting.
- `python -m satnogs_discord_skill show-state` prints the local state file summary.
- `python -m satnogs_discord_skill post-test` sends a small OpenClaw Discord test message.

## Implementation notes

SatNOGS has multiple public services. This skill uses the SatNOGS Network observation endpoints for passes/observations. The SatNOGS DB API is useful for satellite and transmitter metadata, but scheduled observations are read from the Network API.

The code is intentionally dependency-free and uses Python standard library HTTP clients plus the local `openclaw` CLI, so it is easy to run from small cron hosts.
