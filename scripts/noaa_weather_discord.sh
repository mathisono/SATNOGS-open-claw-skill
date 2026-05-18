#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${NOAA_ALERTS_ENV:-$HOME/.config/openclaw/noaa_weather_discord.env}"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a
  source "$ENV_FILE"
  set +a
fi

exec python3 "$(dirname "$0")/noaa_weather_discord.py" "$@"
