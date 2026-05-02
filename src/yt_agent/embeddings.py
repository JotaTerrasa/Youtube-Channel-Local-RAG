from __future__ import annotations

from typing import Protocol

import requests

from .config import Settings


class Embedder(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


class SentenceTransformersEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._encode([text])[0]

    def _encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()


class OllamaEmbedder:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = requests.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": texts},
            timeout=120,
        )
        if response.ok:
            data = response.json()
            if "embeddings" in data:
                return data["embeddings"]

        return [self._legacy_embedding(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def _legacy_embedding(self, text: str) -> list[float]:
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=120,
        )
        if not response.ok:
            raise RuntimeError(f"Ollama embeddings failed: {response.status_code} {response.text}")
        return response.json()["embedding"]


def build_embedder(settings: Settings) -> Embedder:
    provider = settings.embedding_provider.lower().strip()
    if provider in {"sentence-transformers", "sentence_transformers", "local"}:
        return SentenceTransformersEmbedder(settings.embedding_model)
    if provider == "ollama":
        return OllamaEmbedder(settings.ollama_base_url, settings.ollama_embed_model)
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {settings.embedding_provider}")

