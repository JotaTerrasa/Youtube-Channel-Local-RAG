from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value else default


def _load_env_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    whisper_url: str
    chroma_host: str
    chroma_port: int
    chroma_collection: str
    ollama_base_url: str
    ollama_model: str
    embedding_provider: str
    embedding_model: str
    ollama_embed_model: str
    retrieve_k: int
    chunk_max_seconds: float
    chunk_overlap_seconds: float
    chunk_max_chars: int

    @property
    def audio_dir(self) -> Path:
        return self.data_dir / "audio"

    @property
    def transcripts_dir(self) -> Path:
        return self.data_dir / "transcripts"

    def ensure_dirs(self) -> None:
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)


def load_settings(env_file: str | Path = ".env") -> Settings:
    env_path = Path(env_file)
    if env_path.exists():
        _load_env_file(env_path)

    data_dir = Path(os.getenv("APP_DATA_DIR", "./data")).expanduser().resolve()

    return Settings(
        data_dir=data_dir,
        whisper_url=os.getenv("WHISPER_URL", "http://localhost:9000").rstrip("/"),
        chroma_host=os.getenv("CHROMA_HOST", "localhost"),
        chroma_port=_int_env("CHROMA_PORT", 8000),
        chroma_collection=os.getenv("CHROMA_COLLECTION", "youtube_knowledge"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        ollama_model=os.getenv("OLLAMA_MODEL", "gemma4:e2b"),
        embedding_provider=os.getenv("EMBEDDING_PROVIDER", "sentence-transformers"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
        ollama_embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        retrieve_k=_int_env("RETRIEVE_K", 6),
        chunk_max_seconds=_float_env("CHUNK_MAX_SECONDS", 120.0),
        chunk_overlap_seconds=_float_env("CHUNK_OVERLAP_SECONDS", 20.0),
        chunk_max_chars=_int_env("CHUNK_MAX_CHARS", 2600),
    )
