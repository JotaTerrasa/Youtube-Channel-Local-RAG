from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .utils import compact_text, format_timestamp, youtube_timestamp_url


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: dict[str, str | int | float | bool]


def build_chunks(
    transcript: dict[str, Any],
    max_seconds: float,
    overlap_seconds: float,
    max_chars: int,
) -> list[Chunk]:
    video = transcript["video"]
    segments = [
        segment
        for segment in transcript["segments"]
        if segment.get("text") and compact_text(segment["text"])
    ]

    chunks: list[Chunk] = []
    current: list[dict[str, Any]] = []

    def should_flush(next_segment: dict[str, Any]) -> bool:
        if not current:
            return False
        start = float(current[0]["start"])
        projected_end = float(next_segment["end"])
        projected_text = " ".join(segment["text"] for segment in [*current, next_segment])
        return (
            projected_end - start > max_seconds
            or len(projected_text) > max_chars
        )

    def emit(active_segments: list[dict[str, Any]]) -> None:
        if not active_segments:
            return
        start = float(active_segments[0]["start"])
        end = float(active_segments[-1]["end"])
        text = compact_text(" ".join(segment["text"] for segment in active_segments))
        chunk_id = f"{video['video_id']}:{int(start * 1000)}:{int(end * 1000)}"
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                text=text,
                metadata={
                    "video_id": video["video_id"],
                    "title": video["title"],
                    "channel": video.get("channel", ""),
                    "source_url": video["webpage_url"],
                    "timestamp_url": youtube_timestamp_url(video["webpage_url"], start),
                    "start": start,
                    "end": end,
                    "start_time": format_timestamp(start),
                    "end_time": format_timestamp(end),
                    "language": transcript.get("language", ""),
                },
            )
        )

    for segment in segments:
        if should_flush(segment):
            emit(current)
            last_end = float(current[-1]["end"])
            overlap_start = max(0.0, last_end - overlap_seconds)
            current = [
                item
                for item in current
                if float(item["end"]) >= overlap_start
            ]
        current.append(segment)

    emit(current)
    return chunks

