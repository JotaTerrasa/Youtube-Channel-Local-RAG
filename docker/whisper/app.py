import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from faster_whisper import WhisperModel


app = FastAPI(title="CUDA Whisper transcription service")
_model: Optional[WhisperModel] = None


def _settings() -> dict:
    return {
        "model_size_or_path": os.getenv("WHISPER_MODEL", "large-v3"),
        "device": os.getenv("WHISPER_DEVICE", "cuda"),
        "compute_type": os.getenv("WHISPER_COMPUTE_TYPE", "float16"),
        "download_root": os.getenv("WHISPER_DOWNLOAD_ROOT", "/root/.cache/huggingface"),
    }


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        settings = _settings()
        Path(settings["download_root"]).mkdir(parents=True, exist_ok=True)
        _model = WhisperModel(**settings)
    return _model


def _gpu_visible() -> bool:
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "gpu_visible": _gpu_visible(),
        "model_loaded": _model is not None,
        "settings": _settings(),
    }


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: Optional[str] = Form(default=None),
    beam_size: int = Form(default=5),
    vad_filter: bool = Form(default=True),
) -> dict:
    suffix = Path(file.filename or "audio").suffix or ".audio"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        segments_iter, info = get_model().transcribe(
            tmp_path,
            language=language or None,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )

        segments = [
            {
                "start": float(segment.start),
                "end": float(segment.end),
                "text": segment.text.strip(),
            }
            for segment in segments_iter
        ]

        return {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": segments,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if "tmp_path" in locals():
            Path(tmp_path).unlink(missing_ok=True)
