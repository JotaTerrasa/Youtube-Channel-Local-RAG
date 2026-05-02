# Contributing

Este proyecto está pensado como herramienta local. Las contribuciones más útiles suelen estar en:

- Mejoras de ingesta y reanudación.
- Mejor chunking.
- Mejor retrieval.
- Tests de regresión.
- Soporte para más proveedores de embeddings o vector DB.

## Desarrollo Local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
docker compose up -d --build
yt-agent check
```

## Antes de Enviar Cambios

```powershell
python -m compileall src tests
python -m unittest discover -s tests
```

No incluyas datos generados, transcripciones, audios, bases Chroma ni `.env`.

