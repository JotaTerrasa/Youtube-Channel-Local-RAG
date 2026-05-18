# Development

## English

## Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Start services:

```powershell
docker compose up -d --build
```

Start services with NVIDIA CUDA:

```powershell
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d --build
```

Verify:

```powershell
yt-agent check
```

## Tests

```powershell
python -m unittest discover -s tests
```

Compile syntax:

```powershell
python -m compileall src tests
```

## CLI

The entrypoint is defined in `pyproject.toml`:

```toml
[project.scripts]
yt-agent = "yt_agent.cli:main"
```

You can also run it as a module:

```powershell
python -m yt_agent --help
```

## Adding Functionality

The main modules are:

- `cli.py`: arguments and commands.
- `pipeline.py`: ingestion flow.
- `youtube.py`: URL resolution and download with `yt-dlp`.
- `chunking.py`: transcript chunking.
- `embeddings.py`: embedding providers.
- `vectorstore.py`: ChromaDB.
- `graph.py`: LangGraph agent.

Keep changes small and add tests when touching chunking, cache, metadata, or CLI behavior.

## Publishing to GitHub

Before publishing:

```powershell
git status --short
python -m unittest discover -s tests
yt-agent check
```

Do not upload:

- `.env`
- `.venv/`
- `data/audio/`
- `data/transcripts/`
- `data/chroma/`
- `data/whisper-cache/`

These paths are already covered by `.gitignore`.

## First Commit

```powershell
git add .
git commit -m "Initial YouTube RAG agent"
```

Create the GitHub repo and connect the remote:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USER/youtube-channel-rag-agent.git
git push -u origin main
```

For this repository:

```powershell
git remote add origin https://github.com/JotaTerrasa/Youtube-Channel-Local-RAG.git
```

---

## Español

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

Levantar servicios con NVIDIA CUDA:

```powershell
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d --build
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

Mantén los cambios pequeños y añade tests cuando toques chunking, caché, metadatos o comportamiento del CLI.

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

Para este repositorio:

```powershell
git remote add origin https://github.com/JotaTerrasa/Youtube-Channel-Local-RAG.git
```
