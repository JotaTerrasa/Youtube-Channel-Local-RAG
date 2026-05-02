from __future__ import annotations

import argparse
from typing import Sequence

from .config import load_settings


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return

    args.handler(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yt-agent",
        description="YouTube RAG agent with LangGraph, CUDA Whisper, ChromaDB, and Ollama.",
    )
    subparsers = parser.add_subparsers(dest="command")

    check = subparsers.add_parser("check", help="Comprueba Whisper, Chroma y Ollama.")
    check.set_defaults(handler=handle_check)

    ingest = subparsers.add_parser("ingest", help="Ingiere un video, playlist o canal de YouTube.")
    ingest.add_argument("url")
    ingest.add_argument("--max-videos", type=int, default=None)
    ingest.add_argument("--language", default=None, help="Codigo de idioma opcional, por ejemplo es/en.")
    ingest.add_argument("--force-transcribe", action="store_true")
    ingest.add_argument(
        "--skip-cached",
        action="store_true",
        help="Si la transcripcion ya existe, no la reindexa ni descarga audio.",
    )
    ingest.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Detiene la ingesta si falla un video. Por defecto continua con el siguiente.",
    )
    ingest.set_defaults(handler=handle_ingest)

    ask = subparsers.add_parser("ask", help="Pregunta a la base de conocimiento.")
    ask.add_argument("question")
    ask.add_argument("-k", "--top-k", type=int, default=None)
    ask.set_defaults(handler=handle_ask)

    chat = subparsers.add_parser("chat", help="Abre un chat interactivo.")
    chat.add_argument("-k", "--top-k", type=int, default=None)
    chat.set_defaults(handler=handle_chat)

    stats = subparsers.add_parser("stats", help="Muestra estadisticas de la coleccion Chroma.")
    stats.set_defaults(handler=handle_stats)

    return parser


def handle_check(_args: argparse.Namespace) -> None:
    settings = load_settings()
    print(f"Data dir: {settings.data_dir}")

    results = [
        ("Whisper", _check_whisper(settings.whisper_url)),
        ("Chroma", _check_chroma(settings.chroma_host, settings.chroma_port)),
        ("Ollama", _check_ollama(settings.ollama_base_url, settings.ollama_model)),
    ]
    failed = False
    for name, result in results:
        failed = _print_status(name, result) or failed
    if failed:
        raise SystemExit(1)


def handle_ingest(args: argparse.Namespace) -> None:
    from .factory import build_pipeline

    pipeline = build_pipeline()
    results = pipeline.ingest(
        args.url,
        max_videos=args.max_videos,
        language=args.language,
        force_transcribe=args.force_transcribe,
        skip_cached=args.skip_cached,
        continue_on_error=not args.stop_on_error,
        on_progress=lambda message: print(f"-> {message}", flush=True),
    )

    print("\nIngesta completada:")
    for result in results:
        print(f"- {result.title} [{result.video_id}] - {result.status} - {result.chunks} chunks")
        if result.transcript_path:
            print(f"  Transcript: {result.transcript_path}")
        if result.error:
            print(f"  Error: {result.error}")


def handle_ask(args: argparse.Namespace) -> None:
    from .factory import build_agent

    agent = build_agent()
    result = agent.ask(args.question, k=args.top_k)
    print(result["answer"])


def handle_chat(args: argparse.Namespace) -> None:
    from .factory import build_agent

    agent = build_agent()
    print("Chat listo. Escribe 'salir' para terminar.\n")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if question.lower() in {"salir", "exit", "quit"}:
            return
        if not question:
            continue

        result = agent.ask(question, k=args.top_k)
        print(f"\n{result['answer']}\n")


def handle_stats(_args: argparse.Namespace) -> None:
    import chromadb

    settings = load_settings()
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    try:
        collection = client.get_collection(name=settings.chroma_collection)
        count = collection.count()
    except Exception:
        count = 0
    print(f"Chunks en Chroma: {count}")


def _check_whisper(base_url: str) -> tuple[bool, str]:
    import requests

    try:
        response = requests.get(f"{base_url.rstrip('/')}/health", timeout=30)
        response.raise_for_status()
        data = response.json()
        gpu = "GPU visible" if data.get("gpu_visible") else "GPU no visible"
        loaded = "modelo cargado" if data.get("model_loaded") else "modelo aun no cargado"
        return True, f"{gpu}; {loaded}; {data.get('settings', {})}"
    except Exception as exc:
        return False, str(exc)


def _check_chroma(host: str, port: int) -> tuple[bool, str]:
    import requests

    urls = [
        f"http://{host}:{port}/api/v2/heartbeat",
        f"http://{host}:{port}/api/v1/heartbeat",
    ]
    errors = []
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                return True, response.text
            errors.append(f"{url} -> {response.status_code}")
        except Exception as exc:
            errors.append(f"{url} -> {exc}")
    return False, "; ".join(errors)


def _check_ollama(base_url: str, model: str) -> tuple[bool, str]:
    import requests

    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        response.raise_for_status()
        models = [item.get("name") for item in response.json().get("models", [])]
        if model in models:
            return True, f"modelo disponible: {model}"
        return False, f"modelo {model} no aparece en Ollama. Modelos: {', '.join(models)}"
    except Exception as exc:
        return False, str(exc)


def _print_status(name: str, result: tuple[bool, str]) -> bool:
    ok, detail = result
    prefix = "OK" if ok else "ERROR"
    print(f"{prefix} {name}: {detail}")
    return not ok
