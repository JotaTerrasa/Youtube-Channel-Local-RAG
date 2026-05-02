# Desarrollo

## Entorno

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Levantar servicios:

```powershell
docker compose up -d --build
```

Verificar:

```powershell
yt-agent check
```

## Tests

```powershell
python -m unittest discover -s tests
```

Compilar sintaxis:

```powershell
python -m compileall src tests
```

## CLI

El entrypoint está en `pyproject.toml`:

```toml
[project.scripts]
yt-agent = "yt_agent.cli:main"
```

También puedes ejecutarlo como módulo:

```powershell
python -m yt_agent --help
```

## Añadir Funcionalidad

Los módulos principales son:

- `cli.py`: argumentos y comandos.
- `pipeline.py`: flujo de ingesta.
- `youtube.py`: resolución y descarga con `yt-dlp`.
- `chunking.py`: división de transcripciones.
- `embeddings.py`: proveedores de embeddings.
- `vectorstore.py`: ChromaDB.
- `graph.py`: agente LangGraph.

Mantén los cambios pequeños y añade tests cuando toques chunking, cache, metadatos o comportamiento del CLI.

## Publicar en GitHub

Antes de publicar:

```powershell
git status --short
python -m unittest discover -s tests
yt-agent check
```

No subas:

- `.env`
- `.venv/`
- `data/audio/`
- `data/transcripts/`
- `data/chroma/`
- `data/whisper-cache/`

Ya están cubiertos por `.gitignore`.

## Crear el Primer Commit

```powershell
git add .
git commit -m "Initial YouTube RAG agent"
```

Crear repo en GitHub y conectar remoto:

```powershell
git branch -M main
git remote add origin https://github.com/TU_USUARIO/youtube-channel-rag-agent.git
git push -u origin main
```

