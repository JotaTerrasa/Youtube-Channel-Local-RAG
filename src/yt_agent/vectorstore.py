from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import chromadb

from .chunking import Chunk
from .config import Settings
from .embeddings import Embedder


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    metadata: dict[str, Any]
    distance: float | None


class ChromaKnowledgeBase:
    def __init__(self, settings: Settings, embedder: Embedder):
        self.settings = settings
        self.embedder = embedder
        self.client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[Chunk], batch_size: int = 32) -> None:
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            documents = [chunk.text for chunk in batch]
            embeddings = self.embedder.embed_documents(documents)
            self.collection.upsert(
                ids=[chunk.chunk_id for chunk in batch],
                documents=documents,
                metadatas=[chunk.metadata for chunk in batch],
                embeddings=embeddings,
            )

    def search(self, query: str, k: int) -> list[RetrievedChunk]:
        embedding = self.embedder.embed_query(query)
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        return [
            RetrievedChunk(text=document, metadata=metadata or {}, distance=distance)
            for document, metadata, distance in zip(documents, metadatas, distances)
        ]

    def count(self) -> int:
        return self.collection.count()

