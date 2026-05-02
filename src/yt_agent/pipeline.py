from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .chunking import build_chunks
from .config import Settings
from .vectorstore import ChromaKnowledgeBase
from .whisper_client import WhisperClient
from .youtube import VideoAsset, YoutubeIngestor


ProgressCallback = Callable[[str], None]


@dataclass(frozen=True)
class IngestResult:
    video_id: str
    title: str
    chunks: int
    transcript_path: Path | None
    status: str
    error: str | None = None


class IngestPipeline:
    def __init__(
        self,
        settings: Settings,
        knowledge_base: ChromaKnowledgeBase,
        whisper: WhisperClient,
        youtube: YoutubeIngestor,
    ):
        self.settings = settings
        self.knowledge_base = knowledge_base
        self.whisper = whisper
        self.youtube = youtube

    def ingest(
        self,
        url: str,
        max_videos: int | None = None,
        language: str | None = None,
        force_transcribe: bool = False,
        skip_cached: bool = False,
        continue_on_error: bool = True,
        on_progress: ProgressCallback | None = None,
    ) -> list[IngestResult]:
        progress = on_progress or (lambda message: None)
        self.settings.ensure_dirs()

        videos = self.youtube.resolve_videos(url, max_videos=max_videos)
        progress(f"Videos resueltos: {len(videos)}")

        results: list[IngestResult] = []
        for index, video in enumerate(videos, start=1):
            transcript_path = (
                self.settings.transcripts_dir / f"{video.video_id}.json"
                if video.video_id
                else None
            )

            try:
                if transcript_path and transcript_path.exists() and not force_transcribe:
                    if skip_cached:
                        progress(
                            f"[{index}/{len(videos)}] Ya existe transcripcion; saltando: "
                            f"{video.title}"
                        )
                        results.append(
                            IngestResult(
                                video_id=video.video_id or "",
                                title=video.title,
                                chunks=0,
                                transcript_path=transcript_path,
                                status="skipped_cached",
                            )
                        )
                        continue

                    progress(f"Usando transcripcion cacheada: {transcript_path.name}")
                    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
                    status = "cached"
                else:
                    progress(f"[{index}/{len(videos)}] Descargando audio: {video.webpage_url}")
                    asset = self.youtube.download_audio(video)
                    transcript_path = self.settings.transcripts_dir / f"{asset.video_id}.json"
                    progress(f"Transcribiendo con Whisper/CUDA: {asset.title}")
                    transcript = self._transcribe_asset(asset, language=language)
                    transcript_path.write_text(
                        json.dumps(transcript, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    status = "transcribed"

                chunks = build_chunks(
                    transcript,
                    max_seconds=self.settings.chunk_max_seconds,
                    overlap_seconds=self.settings.chunk_overlap_seconds,
                    max_chars=self.settings.chunk_max_chars,
                )
                progress(f"Indexando {len(chunks)} chunks en Chroma")
                self.knowledge_base.upsert_chunks(chunks)

                results.append(
                    IngestResult(
                        video_id=transcript["video"]["video_id"],
                        title=transcript["video"]["title"],
                        chunks=len(chunks),
                        transcript_path=transcript_path,
                        status=status,
                    )
                )
            except Exception as exc:
                if not continue_on_error:
                    raise

                progress(f"[{index}/{len(videos)}] ERROR; continuo con el siguiente: {exc}")
                results.append(
                    IngestResult(
                        video_id=video.video_id or "",
                        title=video.title,
                        chunks=0,
                        transcript_path=transcript_path,
                        status="failed",
                        error=str(exc),
                    )
                )

        return results

    def _transcribe_asset(self, asset: VideoAsset, language: str | None) -> dict:
        transcription = self.whisper.transcribe(asset.audio_path, language=language)
        return {
            "video": {
                "video_id": asset.video_id,
                "title": asset.title,
                "channel": asset.channel,
                "webpage_url": asset.webpage_url,
                "duration": asset.duration,
            },
            "language": transcription.get("language") or "",
            "language_probability": transcription.get("language_probability"),
            "duration": transcription.get("duration"),
            "segments": transcription["segments"],
        }
