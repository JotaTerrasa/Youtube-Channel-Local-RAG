from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class WhisperClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/health", timeout=10)
        response.raise_for_status()
        return response.json()

    def transcribe(
        self,
        audio_path: Path,
        language: str | None = None,
        beam_size: int = 5,
        vad_filter: bool = True,
    ) -> dict[str, Any]:
        data = {
            "beam_size": str(beam_size),
            "vad_filter": "true" if vad_filter else "false",
        }
        if language:
            data["language"] = language

        with audio_path.open("rb") as handle:
            response = requests.post(
                f"{self.base_url}/transcribe",
                data=data,
                files={"file": (audio_path.name, handle)},
                timeout=None,
            )

        if not response.ok:
            raise RuntimeError(f"Whisper failed: {response.status_code} {response.text}")

        return response.json()

