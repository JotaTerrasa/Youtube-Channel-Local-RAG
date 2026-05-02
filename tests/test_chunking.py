import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from yt_agent.chunking import build_chunks
from yt_agent.utils import format_timestamp, youtube_timestamp_url


class ChunkingTests(unittest.TestCase):
    def test_timestamp_formatting(self):
        self.assertEqual(format_timestamp(62), "1:02")
        self.assertEqual(format_timestamp(3661), "1:01:01")

    def test_youtube_timestamp_url(self):
        url = youtube_timestamp_url("https://www.youtube.com/watch?v=abc", 91)
        self.assertEqual(url, "https://www.youtube.com/watch?v=abc&t=91s")

    def test_build_chunks_keeps_video_metadata(self):
        transcript = {
            "video": {
                "video_id": "abc",
                "title": "Demo",
                "channel": "Canal",
                "webpage_url": "https://www.youtube.com/watch?v=abc",
            },
            "language": "es",
            "segments": [
                {"start": 0.0, "end": 10.0, "text": "Primera idea."},
                {"start": 11.0, "end": 30.0, "text": "Segunda idea."},
            ],
        }

        chunks = build_chunks(
            transcript,
            max_seconds=120,
            overlap_seconds=20,
            max_chars=2600,
        )

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].metadata["video_id"], "abc")
        self.assertIn("Primera idea", chunks[0].text)
        self.assertIn("t=0s", chunks[0].metadata["timestamp_url"])


if __name__ == "__main__":
    unittest.main()

