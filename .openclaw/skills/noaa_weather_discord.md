# NOAA Weather Alerts → Discord

Use `scripts/noaa_weather_discord.py` to fetch active California alerts from NOAA and post a compact summary to Discord.

## Defaults

- NOAA source: `https://api.weather.gov/alerts/active?area=CA`
- User-Agent: `kj6dzb open claw weather`
- Discord channel: `1494094633142194176`

## Env vars

- `DISCORD_BOT_TOKEN` — required to post
- `DISCORD_CHANNEL_ID` — optional override
- Or put them in `~/.config/openclaw/noaa_weather_discord.env`

## Run

```bash
bash scripts/noaa_weather_discord.sh
```

## Hourly cron

```cron
0 * * * * cd /path/to/workspace && bash scripts/noaa_weather_discord.sh >> .openclaw/weather_alerts.log 2>&1
```
