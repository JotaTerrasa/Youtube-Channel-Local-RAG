from __future__ import annotations

from .config import Settings, load_settings
from .embeddings import build_embedder
from .graph import YoutubeRagAgent
from .pipeline import IngestPipeline
from .vectorstore import ChromaKnowledgeBase
from .whisper_client import WhisperClient
from .youtube import YoutubeIngestor


def build_knowledge_base(settings: Settings | None = None) -> ChromaKnowledgeBase:
    settings = settings or load_settings()
    return ChromaKnowledgeBase(settings, build_embedder(settings))


def build_agent(settings: Settings | None = None) -> YoutubeRagAgent:
    settings = settings or load_settings()
    return YoutubeRagAgent(settings, build_knowledge_base(settings))


def build_pipeline(settings: Settings | None = None) -> IngestPipeline:
    settings = settings or load_settings()
    settings.ensure_dirs()
    knowledge_base = build_knowledge_base(settings)
    return IngestPipeline(
        settings=settings,
        knowledge_base=knowledge_base,
        whisper=WhisperClient(settings.whisper_url),
        youtube=YoutubeIngestor(settings.audio_dir),
    )

