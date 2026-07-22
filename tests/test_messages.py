import unittest

from satnogs_discord_skill.messages import (
    build_completion_embed,
    build_upcoming_embed,
    completion_pass_button,
    completion_waterfall_media,
    duration_text,
    format_completion_message,
    format_upcoming_message,
    frequency_mhz,
    status_emoji,
)
from satnogs_discord_skill.timeutils import parse_datetime


OBS = {
    "id": 42,
    "start": "2026-07-05T12:00:00Z",
    "end": "2026-07-05T12:10:30Z",
    "ground_station": 1234,
    "station_name": "Test Station",
    "sat_id": "TESTSAT",
    "norad_cat_id": 99999,
    "transmitter_mode": "FM",
    "transmitter_downlink_low": 145_800_000,
    "transmitter_description": "Test downlink",
    "max_altitude": 45.123,
    "rise_azimuth": 10,
    "set_azimuth": 270,
    "status": "future",
}


class MessageTests(unittest.TestCase):
    def test_frequency_mhz(self):
        self.assertEqual(frequency_mhz(145_800_000), "145.800 MHz")
        self.assertEqual(frequency_mhz(None), "unknown")

    def test_duration_text(self):
        self.assertEqual(duration_text(parse_datetime(OBS["start"]), parse_datetime(OBS["end"])), "10m 30s")

    def test_status_emoji(self):
        self.assertEqual(status_emoji("good"), "✅")
        self.assertEqual(status_emoji("failed"), "⚠️")

    def test_upcoming_embed_contains_observation_link(self):
        embed = build_upcoming_embed(OBS, api_base_url="https://network.satnogs.org", tz_name="UTC")
        self.assertIn("Upcoming SatNOGS pass", embed["title"])
        self.assertEqual(embed["url"], "https://network.satnogs.org/observations/42/")
        self.assertTrue(embed["fields"])

    def test_completion_embed_has_status_and_links(self):
        obs = dict(OBS, status="good", waterfall="https://example.test/waterfall.png", demoddata=[{"payload_demod": "x"}])
        embed = build_completion_embed(obs, api_base_url="https://network.satnogs.org", tz_name="UTC")
        self.assertIn("complete", embed["title"])
        values = "\n".join(field["value"] for field in embed["fields"])
        self.assertIn("✅ good", values)
        self.assertIn("Waterfall", values)
        self.assertIn("1", values)

    def test_upcoming_openclaw_message(self):
        message = format_upcoming_message(OBS, api_base_url="https://network.satnogs.org", tz_name="UTC")
        self.assertIn("Upcoming SatNOGS pass", message)
        self.assertIn("Observation #42", message)
        self.assertIn("https://network.satnogs.org/observations/42/", message)
        self.assertLessEqual(len(message), 1900)

    def test_completion_openclaw_message(self):
        obs = dict(
            OBS,
            status="good",
            waterfall="https://example.test/waterfall.png",
            archive_url="https://example.test/audio.ogg",
            payload="https://example.test/payload.txt",
            demoddata=[{"payload_demod": "x"}],
        )
        message = format_completion_message(obs, api_base_url="https://network.satnogs.org", tz_name="UTC")
        self.assertIn("SatNOGS pass complete", message)
        self.assertIn("Final status", message)
        self.assertIn("good", message)
        self.assertIn("https://network.satnogs.org/observations/42/", message)
        self.assertNotIn("https://example.test/waterfall.png", message)
        self.assertNotIn("https://example.test/audio.ogg", message)
        self.assertNotIn("https://example.test/payload.txt", message)

    def test_completion_waterfall_media(self):
        obs = dict(OBS, waterfall="https://example.test/waterfall.png")
        self.assertEqual(completion_waterfall_media(obs), "https://example.test/waterfall.png")
        self.assertIsNone(completion_waterfall_media(OBS))

    def test_completion_pass_button(self):
        presentation = completion_pass_button(OBS, api_base_url="https://network.satnogs.org")
        button = presentation["blocks"][0]["buttons"][0]
        self.assertEqual(button["label"], "Open pass")
        self.assertEqual(button["url"], "https://network.satnogs.org/observations/42/")


if __name__ == "__main__":
    unittest.main()
