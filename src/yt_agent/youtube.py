from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VideoRef:
    video_id: str | None
    title: str
    channel: str
    webpage_url: str
    duration: float | None


@dataclass(frozen=True)
class VideoAsset:
    video_id: str
    title: str
    channel: str
    webpage_url: str
    duration: float | None
    audio_path: Path
    raw_info: dict[str, Any]


class YoutubeIngestor:
    def __init__(self, audio_dir: Path):
        self.audio_dir = audio_dir
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def resolve_videos(self, url: str, max_videos: int | None = None) -> list[VideoRef]:
        from yt_dlp import YoutubeDL

        opts = {
            "extract_flat": "in_playlist",
            "ignoreerrors": True,
            "quiet": True,
            "skip_download": True,
        }

        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        entries = info.get("entries") if isinstance(info, dict) else None
        if not entries:
            return [self._video_ref(info, fallback_url=url)]

        videos: list[VideoRef] = []
        for entry in entries:
            if not entry:
                continue
            video = self._video_ref(entry, fallback_url=url)
            if video.webpage_url:
                videos.append(video)
            if max_videos and len(videos) >= max_videos:
                break

        return videos

    def resolve_video_urls(self, url: str, max_videos: int | None = None) -> list[str]:
        return [video.webpage_url for video in self.resolve_videos(url, max_videos=max_videos)]

    def download_audio(self, video: str | VideoRef) -> VideoAsset:
        from yt_dlp import YoutubeDL

        url = video.webpage_url if isinstance(video, VideoRef) else video
        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "ignoreerrors": False,
            "noplaylist": True,
            "outtmpl": str(self.audio_dir / "%(id)s.%(ext)s"),
            "quiet": False,
            "windowsfilenames": True,
        }

        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_path = self._downloaded_path(ydl, info)

        return VideoAsset(
            video_id=str(info["id"]),
            title=info.get("title") or info["id"],
            channel=info.get("channel") or info.get("uploader") or "",
            webpage_url=info.get("webpage_url") or url,
            duration=info.get("duration"),
            audio_path=audio_path,
            raw_info=info,
        )

    @staticmethod
    def _entry_url(entry: dict[str, Any]) -> str | None:
        if entry.get("webpage_url"):
            return str(entry["webpage_url"])
        if entry.get("url") and str(entry["url"]).startswith("http"):
            return str(entry["url"])
        if entry.get("id"):
            return f"https://www.youtube.com/watch?v={entry['id']}"
        return None

    def _downloaded_path(self, ydl: Any, info: dict[str, Any]) -> Path:
        for download in info.get("requested_downloads", []):
            filepath = download.get("filepath") or download.get("_filename")
            if filepath and Path(filepath).exists():
                return Path(filepath).resolve()

        prepared = Path(ydl.prepare_filename(info))
        if prepared.exists():
            return prepared.resolve()

        matches = sorted(self.audio_dir.glob(f"{info['id']}.*"))
        if matches:
            return matches[0].resolve()

        raise FileNotFoundError(f"Could not find downloaded audio for {info['id']}")

    def _video_ref(self, info: dict[str, Any], fallback_url: str) -> VideoRef:
        video_id = str(info["id"]) if info.get("id") else None
        webpage_url = self._entry_url(info) or fallback_url
        return VideoRef(
            video_id=video_id,
            title=info.get("title") or video_id or webpage_url,
            channel=info.get("channel") or info.get("uploader") or "",
            webpage_url=webpage_url,
            duration=info.get("duration"),
        )
