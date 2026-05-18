# SATNOGS Open Claw Skill

Local-model-friendly SatNOGS + Discord utilities.

## Skills

- `satnogs_984_passes` — station 984 schedule + completion posts
- `satnogs_post_report` — formats one SatNOGS observation
- `noaa_weather_discord` — NOAA alerts to Discord

## SatNOGS 984

- 6:00 a.m. daily schedule post
- hourly completion check
- tracks passes scheduled later in the day

## Files

- `scripts/satnogs_984_daily_report.py`
- `scripts/satnogs_984_completion_report.py`
- `scripts/satnogs_984_common.py`
- `scripts/satnogs_post_report.py`
- `scripts/noaa_weather_discord.py`

## Discord

- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID` (default: `1494094633142194176`)

## Cron

```cron
0 6 * * * cd /path/to/workspace && bash scripts/satnogs_984_daily.sh >> .openclaw/satnogs_984.log 2>&1
0 * * * * cd /path/to/workspace && bash scripts/satnogs_984_updates.sh >> .openclaw/satnogs_984.log 2>&1
0 * * * * cd /path/to/workspace && bash scripts/noaa_weather_discord.sh >> .openclaw/weather_alerts.log 2>&1
```

## Notes

- Uses the public SatNOGS Network API.
- Output is plain Markdown for Discord.
- State lives in `.openclaw/satnogs_984_state.json`.
