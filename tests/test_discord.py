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

    def test_dry_run_includes_media_argument(self):
        sender = OpenClawDiscord("channel:1494094633142194176", dry_run=True)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            sender.send_message(
                "hello",
                media="https://example.test/waterfall.png",
                presentation={"blocks": [{"type": "buttons", "buttons": [{"label": "Open pass", "url": "https://network.satnogs.org/observations/42/"}]}]},
            )
        data = json.loads(buffer.getvalue())
        self.assertIn("--media https://example.test/waterfall.png", data["command"])
        self.assertIn("--presentation", data["command"])
        self.assertIn("https://network.satnogs.org/observations/42/", data["command"])
        self.assertEqual(data["media"], "https://example.test/waterfall.png")
        self.assertEqual(data["presentation"]["blocks"][0]["buttons"][0]["label"], "Open pass")


if __name__ == "__main__":
    unittest.main()
