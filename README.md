# SATNOGS Open Claw Skill

OpenClaw skill set for SatNOGS pass reporting and Discord updates.

## Overview

This repo contains small scripts and skills for:

- daily SatNOGS schedule posts
- hourly completion updates
- compact pass formatting
- NOAA weather alerts to Discord

The scripts are model-agnostic. You can run them from a **local model** agent, and they only need Python + network access.

## Skills

- `satnogs_984_passes` — daily + hourly station 984 reporting
- `satnogs_post_report` — formats a SatNOGS post-pass report
- `noaa_weather_discord` — NOAA weather alerts to Discord

## SatNOGS 984 workflow

### Morning schedule post

- Runs at **6:00 a.m.**
- Pulls scheduled passes for **ground station 984**
- Posts the day’s list to Discord
- Saves pass IDs so later updates can be matched

### Hourly completion updates

- Runs every hour
- Checks for completed passes from the saved schedule
- Also catches passes scheduled after the morning list
- Posts new completions to Discord

### Report formatting

- Renders compact SatNOGS post-pass summaries
- Useful for Discord, logs, or manual review

## Main files

- `scripts/satnogs_984_daily_report.py`
- `scripts/satnogs_984_completion_report.py`
- `scripts/satnogs_984_common.py`
- `scripts/satnogs_post_report.py`
- `scripts/noaa_weather_discord.py`

## Discord setup

Uses:

- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID` (defaults to `1494094633142194176`)

Optional env file:

- `~/.config/openclaw/noaa_weather_discord.env`

## Cron jobs

### SatNOGS 984

```cron
0 6 * * * cd /path/to/workspace && bash scripts/satnogs_984_daily.sh >> .openclaw/satnogs_984.log 2>&1
0 * * * * cd /path/to/workspace && bash scripts/satnogs_984_updates.sh >> .openclaw/satnogs_984.log 2>&1
```

### NOAA alerts

```cron
0 * * * * cd /path/to/workspace && bash scripts/noaa_weather_discord.sh >> .openclaw/weather_alerts.log 2>&1
```

## SatNOGS API behavior

- Uses the public SatNOGS Network API
- Station 984 is the target ground station
- Morning report stores scheduled observation IDs
- Hourly report compares new observations against that saved state
- New same-day passes are included when they appear later

## Local state

Saved under:

- `.openclaw/satnogs_984_state.json`

## Notes

- The SatNOGS API can rate-limit requests, so the scripts use retry/backoff.
- Output is plain Markdown so it posts cleanly to Discord.
- If you want a different station, swap the station ID in the helper and scripts.
