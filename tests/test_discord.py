import io
import json
import unittest
from contextlib import redirect_stdout

from satnogs_discord_skill.discord import OpenClawDiscord


class OpenClawDiscordTests(unittest.TestCase):
    def test_dry_run_prints_openclaw_command(self):
        sender = OpenClawDiscord("channel:1494094633142194176", dry_run=True)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            sender.send_message("hello")
        data = json.loads(buffer.getvalue())
        self.assertTrue(data["dry_run"])
        self.assertIn("openclaw message send", data["command"])
        self.assertIn("channel:1494094633142194176", data["command"])
        self.assertEqual(data["message"], "hello")


if __name__ == "__main__":
    unittest.main()
