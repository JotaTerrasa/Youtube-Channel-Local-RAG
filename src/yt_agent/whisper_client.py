from __future__ import annotations

from pathlib import Path
import time
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
        retries: int = 2,
        retry_delay_seconds: float = 10.0,
    ) -> dict[str, Any]:
        data = {
            "beam_size": str(beam_size),
            "vad_filter": "true" if vad_filter else "false",
        }
        if language:
            data["language"] = language

        last_error: Exception | None = None
        for attempt in range(1, retries + 2):
            try:
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
            except (
                requests.ConnectionError,
                requests.Timeout,
                requests.HTTPError,
                RuntimeError,
            ) as exc:
                last_error = exc
                if attempt > retries:
                    break
                time.sleep(retry_delay_seconds * attempt)

        raise RuntimeError(f"Whisper transcription failed after retries: {last_error}")
