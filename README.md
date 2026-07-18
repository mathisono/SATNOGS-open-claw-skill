# SATNOGS OpenClaw Skill

OpenClaw skill and cron-friendly Python utility for monitoring a SatNOGS ground station and posting pass notifications to Discord using OpenClaw's Discord connector.

Target behavior:

1. Read future SatNOGS observations for a configured ground station ID.
2. Post each newly discovered pass to a Discord channel through the same OpenClaw CLI process used by [`goes-satellite-gif`](https://github.com/mathisono/goes-satellite-gif): `openclaw message send --channel discord --target channel:<id> --message ...`.
3. Remember what was announced.
4. After each pass ends, check SatNOGS again and post a completion summary with status, signal/waterfall information, demodulated data count, and useful links.

## Repository layout

```text
SKILL.md                         OpenClaw skill instructions
satnogs_discord_skill/           Dependency-free Python implementation
scripts/satnogs-discord-cron.sh  Cron wrapper
examples/env.example             Configuration template
examples/systemd/                Optional systemd timer/service
.github/workflows/ci.yml         Unit-test workflow
```

## Requirements

- Python 3.11 or newer.
- OpenClaw CLI available as `openclaw` for the user that runs the job.
- OpenClaw Discord integration configured and able to post to the target Discord channel.
- Outbound HTTPS access to `https://network.satnogs.org`.
- A SatNOGS ground station ID.
- A SatNOGS API token, recommended for reliable authenticated API requests.

No Python packages are required for runtime. The implementation uses only the Python standard library and the local `openclaw` command.

## Configuration

Copy the example environment file and fill in your values:

```bash
cp examples/env.example .env
$EDITOR .env
set -a
. ./.env
set +a
```

Required for station 984:

```bash
SATNOGS_STATION_ID=984
SATNOGS_API_TOKEN=<paste your SatNOGS API token here>
OPENCLAW_DISCORD_TARGET=channel:1494094633142194176
```

You may use `DISCORD_CHANNEL_ID=1494094633142194176` instead of `OPENCLAW_DISCORD_TARGET`; the skill will convert it to `channel:1494094633142194176`.

Optional:

```bash
SATNOGS_LOOKAHEAD_HOURS=24
SATNOGS_COMPLETION_GRACE_MINUTES=5
SATNOGS_TIMEZONE=America/Los_Angeles
SATNOGS_STATE_FILE=.satnogs_state.json
SATNOGS_API_BASE_URL=https://network.satnogs.org
OPENCLAW_DISCORD_CHANNEL=discord
OPENCLAW_COMMAND=openclaw
SATNOGS_MAX_OBSERVATIONS=100
```

Do not commit `.env`. Treat `SATNOGS_API_TOKEN` like a password.

## Discord posting model

This skill does not use Discord webhooks. It shells out to OpenClaw's Discord connector:

```bash
openclaw message send \
  --channel discord \
  --target channel:1494094633142194176 \
  --message "SatNOGS pass update..."
```

Verify OpenClaw Discord before running live posts:

```bash
openclaw channels status --deep
openclaw message send --channel discord --target channel:1494094633142194176 --message "SatNOGS monitor test"
```

## Dry run

Always test with `--dry-run` before sending to Discord:

```bash
python -m satnogs_discord_skill once --dry-run
```

Dry-run mode fetches SatNOGS data and prints the exact `openclaw message send` commands instead of posting them.

## Run once

```bash
python -m satnogs_discord_skill once
```

`once` performs both halves of the workflow:

- announces future observations that have not already been announced;
- checks previously announced observations after their end time and posts completion summaries when SatNOGS reports a non-`future` status.

## Useful commands

```bash
python -m satnogs_discord_skill announce-upcoming
python -m satnogs_discord_skill check-completed
python -m satnogs_discord_skill list-upcoming
python -m satnogs_discord_skill show-state
python -m satnogs_discord_skill post-test
```

All commands accept CLI overrides, for example:

```bash
python -m satnogs_discord_skill once \
  --station-id 984 \
  --api-token "$SATNOGS_API_TOKEN" \
  --discord-target channel:1494094633142194176 \
  --lookahead-hours 48 \
  --timezone America/Los_Angeles \
  --state-file /var/lib/satnogs-discord/state.json
```

## Cron

Edit your crontab with `crontab -e` for the same Linux user that has working OpenClaw Discord access:

```cron
*/10 * * * * cd /path/to/SATNOGS-open-claw-skill && . ./.env && ./scripts/satnogs-discord-cron.sh >> /var/log/satnogs-discord.log 2>&1
```

The state file prevents duplicate announcements, so running every 5-10 minutes is safe.

## systemd timer

Copy the example units and adjust `WorkingDirectory`, `EnvironmentFile`, and user/group values:

```bash
sudo cp examples/systemd/satnogs-discord.service /etc/systemd/system/
sudo cp examples/systemd/satnogs-discord.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now satnogs-discord.timer
```

## How completion detection works

When an upcoming observation is announced, the skill stores its observation ID and end time. On later runs, if the end time plus `SATNOGS_COMPLETION_GRACE_MINUTES` has passed, the skill fetches that observation again from SatNOGS. It posts the completion summary once SatNOGS returns a status other than `future`.

## State file

Default state file:

```text
.satnogs_state.json
```

The file contains announced observation IDs, end times, and completion-posting markers. It is safe to delete if you want to re-announce all observations in the lookahead window.

## Development

Run tests:

```bash
python -m unittest discover -s tests
```

Run formatting or linting with your preferred tools. The project intentionally avoids runtime Python dependencies.

## Notes on SatNOGS APIs

The original repository note pointed at SatNOGS DB. SatNOGS DB is useful for satellite/transmitter/TLE metadata, while scheduled station observations are exposed by SatNOGS Network. This implementation uses SatNOGS Network for pass monitoring and leaves DB metadata enrichment as a future extension.

## License

CC0-1.0, matching the original repository license.
