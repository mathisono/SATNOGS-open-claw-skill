# SatNOGS 984 Pass Reports

Local-model-friendly skill for station **984**.

## What it does

1. `scripts/satnogs_984_daily_report.py`
   - runs at **6:00 a.m.**
   - posts the day's scheduled passes
   - saves scheduled pass IDs for later tracking

2. `scripts/satnogs_984_completion_report.py`
   - runs hourly
   - checks for completed passes from the saved schedule
   - also picks up passes newly scheduled later in the day

## Discord

Uses the existing bot token and channel defaults:

- channel: `1494094633142194176`
- env: `DISCORD_BOT_TOKEN`
- wrapper sources `~/.config/openclaw/noaa_weather_discord.env` if present

## State

Saved to:

- `.openclaw/satnogs_984_state.json`

## Cron

```cron
0 6 * * * cd /path/to/workspace && bash scripts/satnogs_984_daily.sh >> .openclaw/satnogs_984.log 2>&1
0 * * * * cd /path/to/workspace && bash scripts/satnogs_984_updates.sh >> .openclaw/satnogs_984.log 2>&1
```

## Notes

- Designed to run under a local model or any OpenClaw agent.
- Uses SatNOGS public API data and plain Markdown output.
