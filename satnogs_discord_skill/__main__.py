"""Module entrypoint for `python -m satnogs_discord_skill`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
