# SatNOGS 984 Pass Reports

Local-model-friendly skill for station **984**.

## What it does

- **6:00 a.m.** daily schedule post
- hourly completion check
- tracks passes scheduled later in the day

## Discord

- channel: `1494094633142194176`
- env: `DISCORD_BOT_TOKEN`
- wrapper sources `~/.config/openclaw/noaa_weather_discord.env` if present

## State

- `.openclaw/satnogs_984_state.json`

## Cron

```cron
0 6 * * * cd /path/to/workspace && bash scripts/satnogs_984_daily.sh >> .openclaw/satnogs_984.log 2>&1
0 * * * * cd /path/to/workspace && bash scripts/satnogs_984_updates.sh >> .openclaw/satnogs_984.log 2>&1
```
