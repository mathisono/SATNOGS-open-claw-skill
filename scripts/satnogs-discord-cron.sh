#!/usr/bin/env bash
set -euo pipefail

# Run from the repository root or set SATNOGS_SKILL_DIR.
cd "${SATNOGS_SKILL_DIR:-$(pwd)}"
exec "${PYTHON:-python3}" -m satnogs_discord_skill once
