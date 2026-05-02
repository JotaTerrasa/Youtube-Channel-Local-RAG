import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from yt_agent.config import Settings
from yt_agent.pipeline import IngestPipeline
from yt_agent.youtube import VideoRef


class FakeKnowledgeBase:
    def __init__(self):
        self.upserted = []

    def upsert_chunks(self, chunks):
        self.upserted.extend(chunks)


class FakeWhisper:
    def transcribe(self, _audio_path, language=None):
        return {"language": language or "es", "segments": []}


class FakeYoutube:
    def __init__(self):
        self.downloads = 0

    def resolve_videos(self, _url, max_videos=None):
        return [
            VideoRef(
                video_id="abc",
                title="Video cacheado",
                channel="Canal",
                webpage_url="https://www.youtube.com/watch?v=abc",
                duration=10,
            )
        ]

    def download_audio(self, _video):
        self.downloads += 1
        return SimpleNamespace()


class FailingYoutube(FakeYoutube):
    def download_audio(self, _video):
        self.downloads += 1
        raise RuntimeError("download failed")


class PipelineTests(unittest.TestCase):
    def test_skip_cached_avoids_download_and_indexing(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = self._settings(Path(tmp))
            settings.ensure_dirs()
            transcript_path = settings.transcripts_dir / "abc.json"
            transcript_path.write_text(
                json.dumps(
                    {
                        "video": {
                            "video_id": "abc",
                            "title": "Video cacheado",
                            "channel": "Canal",
                            "webpage_url": "https://www.youtube.com/watch?v=abc",
                            "duration": 10,
                        },
                        "language": "es",
                        "segments": [{"start": 0, "end": 2, "text": "Texto existente"}],
                    }
                ),
                encoding="utf-8",
            )

            youtube = FakeYoutube()
            kb = FakeKnowledgeBase()
            pipeline = IngestPipeline(settings, kb, FakeWhisper(), youtube)

            results = pipeline.ingest(
                "https://www.youtube.com/@canal/videos",
                skip_cached=True,
            )

            self.assertEqual(youtube.downloads, 0)
            self.assertEqual(kb.upserted, [])
            self.assertEqual(results[0].status, "skipped_cached")

    def test_ingest_continues_when_video_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = self._settings(Path(tmp))
            settings.ensure_dirs()
            youtube = FailingYoutube()
            kb = FakeKnowledgeBase()
            pipeline = IngestPipeline(settings, kb, FakeWhisper(), youtube)

            results = pipeline.ingest("https://www.youtube.com/@canal/videos")

            self.assertEqual(youtube.downloads, 1)
            self.assertEqual(results[0].status, "failed")
            self.assertIn("download failed", results[0].error)

    def test_ingest_can_stop_on_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = self._settings(Path(tmp))
            settings.ensure_dirs()
            pipeline = IngestPipeline(settings, FakeKnowledgeBase(), FakeWhisper(), FailingYoutube())

            with self.assertRaises(RuntimeError):
                pipeline.ingest(
                    "https://www.youtube.com/@canal/videos",
                    continue_on_error=False,
                )

    @staticmethod
    def _settings(data_dir: Path) -> Settings:
        return Settings(
            data_dir=data_dir,
            whisper_url="http://localhost:9000",
            chroma_host="localhost",
            chroma_port=8000,
            chroma_collection="test",
            ollama_base_url="http://localhost:11434",
            ollama_model="gemma4:e2b",
            embedding_provider="sentence-transformers",
            embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            ollama_embed_model="nomic-embed-text",
            retrieve_k=6,
            chunk_max_seconds=120,
            chunk_overlap_seconds=20,
            chunk_max_chars=2600,
        )


if __name__ == "__main__":
    unittest.main()
