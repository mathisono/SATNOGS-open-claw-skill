import argparse
import os
import unittest
from unittest.mock import patch

from satnogs_discord_skill.config import ConfigError, load_config


def args(**overrides):
    values = dict(
        station_id=None,
        discord_target=None,
        discord_channel_id=None,
        discord_channel=None,
        openclaw_command=None,
        api_base_url=None,
        api_token=None,
        state_file=None,
        lookahead_hours=None,
        completion_grace_minutes=None,
        timezone=None,
        max_observations=None,
        dry_run=False,
    )
    values.update(overrides)
    return argparse.Namespace(**values)


class ConfigTests(unittest.TestCase):
    def test_loads_required_values_from_env_for_dry_run(self):
        with patch.dict(os.environ, {"SATNOGS_STATION_ID": "123"}, clear=True):
            cfg = load_config(args(dry_run=True))
        self.assertEqual(cfg.station_id, 123)
        self.assertTrue(cfg.dry_run)

    def test_builds_openclaw_target_from_channel_id(self):
        with patch.dict(os.environ, {"SATNOGS_STATION_ID": "123", "DISCORD_CHANNEL_ID": "1494094633142194176"}, clear=True):
            cfg = load_config(args())
        self.assertEqual(cfg.discord_target, "channel:1494094633142194176")
        self.assertEqual(cfg.discord_channel, "discord")

    def test_accepts_explicit_openclaw_target(self):
        with patch.dict(os.environ, {"SATNOGS_STATION_ID": "123", "OPENCLAW_DISCORD_TARGET": "channel:abc"}, clear=True):
            cfg = load_config(args())
        self.assertEqual(cfg.discord_target, "channel:abc")

    def test_missing_station_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigError):
                load_config(args(dry_run=True))

    def test_show_state_can_load_without_station_or_discord(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = load_config(args(), require_station=False, require_discord=False)
        self.assertEqual(cfg.station_id, 0)
        self.assertIsNone(cfg.discord_target)


if __name__ == "__main__":
    unittest.main()
