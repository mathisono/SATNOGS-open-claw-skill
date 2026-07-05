import argparse
import os
import unittest
from unittest.mock import patch

from satnogs_discord_skill.config import ConfigError, load_config


class ConfigTests(unittest.TestCase):
    def test_loads_required_values_from_env_for_dry_run(self):
        args = argparse.Namespace(
            station_id=None,
            discord_webhook_url=None,
            api_base_url=None,
            api_token=None,
            state_file=None,
            lookahead_hours=None,
            completion_grace_minutes=None,
            timezone=None,
            max_observations=None,
            discord_username=None,
            discord_avatar_url=None,
            dry_run=True,
        )
        with patch.dict(os.environ, {"SATNOGS_STATION_ID": "123"}, clear=True):
            cfg = load_config(args)
        self.assertEqual(cfg.station_id, 123)
        self.assertTrue(cfg.dry_run)

    def test_missing_station_raises(self):
        args = argparse.Namespace(station_id=None, dry_run=True)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigError):
                load_config(args)


if __name__ == "__main__":
    unittest.main()
