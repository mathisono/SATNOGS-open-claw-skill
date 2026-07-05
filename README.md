# SATNOGS OpenClaw Skill

OpenClaw skill and cron-friendly Python utility for monitoring a SatNOGS ground station and posting pass notifications to Discord.

Target behavior:

1. Read future SatNOGS observations for a configured ground station ID.
2. Post each newly discovered pass to a Discord channel such as `satalite-data` / `satellite-data` through a channel webhook.
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
- Outbound HTTPS access to `https://network.satnogs.org` and Discord webhooks.
- A SatNOGS ground station ID.
- A Discord webhook URL created in the target Discord channel.

No Python packages are required for runtime. The implementation uses only the Python standard library.

## Configuration

Copy the example environment file and fill in your values:

```bash
cp examples/env.example .env
$EDITOR .env
set -a
. ./.env
set +a
```

Required:

```bash
SATNOGS_STATION_ID=1234
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

Optional:

```bash
SATNOGS_LOOKAHEAD_HOURS=24
SATNOGS_COMPLETION_GRACE_MINUTES=5
SATNOGS_TIMEZONE=UTC
SATNOGS_STATE_FILE=.satnogs_state.json
SATNOGS_API_BASE_URL=https://network.satnogs.org
SATNOGS_API_TOKEN=
DISCORD_USERNAME=SatNOGS Pass Bot
DISCORD_AVATAR_URL=
```

The webhook is channel-specific. To post to `satalite-data`, create the webhook in that Discord channel and use that webhook URL.

## Dry run

Always test with `--dry-run` before sending to Discord:

```bash
python -m satnogs_discord_skill once --dry-run
```

Dry-run mode fetches SatNOGS data and prints the Discord payloads instead of posting them.

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
python -m satnogs_discord_skill list-upcoming --dry-run
python -m satnogs_discord_skill show-state
python -m satnogs_discord_skill post-test
```

All commands accept CLI overrides, for example:

```bash
python -m satnogs_discord_skill once \
  --station-id 1234 \
  --lookahead-hours 48 \
  --timezone America/Los_Angeles \
  --state-file /var/lib/satnogs-discord/state.json
```

## Cron

Edit your crontab with `crontab -e`:

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

Run formatting or linting with your preferred tools. The project intentionally avoids runtime dependencies.

## Notes on SatNOGS APIs

The original repository note pointed at SatNOGS DB. SatNOGS DB is useful for satellite/transmitter/TLE metadata, while scheduled station observations are exposed by SatNOGS Network. This implementation uses SatNOGS Network for pass monitoring and leaves DB metadata enrichment as a future extension.

## License

CC0-1.0, matching the original repository license.
