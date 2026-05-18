#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${SATNOGS_ENV:-$HOME/.config/openclaw/noaa_weather_discord.env}"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

cd "$(dirname "$0")"
exec python3 satnogs_984_completion_report.py
