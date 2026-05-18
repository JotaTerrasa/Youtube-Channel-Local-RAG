# Troubleshooting

## English

## `yt-agent check` Says Whisper Does Not Respond

Check containers:

```powershell
docker compose ps
```

Start services:

```powershell
docker compose up -d --build
```

If you are on Windows/Linux with NVIDIA and want CUDA:

```powershell
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d --build
```

Inspect logs:

```powershell
docker compose logs -f whisper
```

## Whisper Does Not See the GPU

This only applies if you started with `docker-compose.cuda.yml`. Check CUDA on the host:

```powershell
nvidia-smi
```

Check that Docker Desktop has GPU support enabled. On WSL2/Windows, also verify that the NVIDIA runtime is available to Docker.

The healthcheck should show:

```text
GPU visible
```

## Whisper Closes the Connection During Ingestion

If you see something like:

```text
RemoteDisconnected: Remote end closed connection without response
```

it usually means that the Whisper service inside Docker closed the connection during a transcription. This can happen if the container restarts, the GPU is busy, the audio is long, or the model takes too long to respond.

Ingestion saves each completed transcript in `data/transcripts`, so you can resume without losing previous work:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es
```

By default, if a specific video fails, ingestion continues with the next one. If you prefer to stop at the first error:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es --stop-on-error
```

To process only videos without cached transcripts:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es --skip-cached
```

If the error repeats on long videos, temporarily lower the Whisper model. In CPU mode the default is already `medium`; in CUDA mode you can set `WHISPER_MODEL` in `.env` to `medium` and recreate the service.

## The First Transcription Takes a Long Time

This is normal. The first transcription downloads the Whisper model configured in Docker Compose into `data/whisper-cache`. CPU mode uses `medium` by default; CUDA mode uses `large-v3`.

To use a smaller model, change:

```yaml
WHISPER_MODEL: medium
```

or:

```yaml
WHISPER_MODEL: small
```

Then recreate:

```powershell
docker compose up -d --build --force-recreate whisper
```

In CUDA mode:

```powershell
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d --build --force-recreate whisper
```

## macOS and CUDA

macOS does not support CUDA. Use the base Compose setup:

```bash
docker compose up -d --build
```

This runs Whisper on CPU with `WHISPER_COMPUTE_TYPE=int8`. It is slower than CUDA, but compatible. If you need faster Apple Silicon transcription with Metal/MLX, this would require a separate backend based on `mlx-whisper`.

## Ollama Is Not Installed

Install it from the official page:

- Windows: [ollama.com/download/windows](https://ollama.com/download/windows)
- macOS: [ollama.com/download/mac](https://ollama.com/download/mac)
- Linux: [ollama.com/download/linux](https://ollama.com/download/linux)
- Official quickstart: [docs.ollama.com/quickstart](https://docs.ollama.com/quickstart)

Windows PowerShell:

```powershell
irm https://ollama.com/install.ps1 | iex
```

Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Then:

```powershell
ollama list
```

If that command responds, Ollama is installed and reachable.

## Ollama Does Not Have `gemma4:e2b`

```powershell
ollama pull gemma4:e2b
```

Check:

```powershell
ollama list
```

## `gemma4:e2b` Is Not an Embedding Model

Correct. In this project `gemma4:e2b` is used as the LLM. Embeddings are generated with SentenceTransformers by default.

If you want to use Ollama for embeddings:

```powershell
ollama pull nomic-embed-text
```

And in `.env`:

```dotenv
EMBEDDING_PROVIDER=ollama
OLLAMA_EMBED_MODEL=nomic-embed-text
```

## Chroma Does Not Respond

```powershell
docker compose logs -f chroma
docker compose restart chroma
```

Persistence lives in:

```text
data/chroma/
```

## Reindex From Existing Transcripts

Rerunning ingestion without `--skip-cached` reuses existing transcripts and indexes the chunks in Chroma again:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es
```

## Process Only New Videos

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es --skip-cached
```

## YouTube Blocks or Limits Downloads

`yt-dlp` depends on YouTube changes. Update dependencies:

```powershell
pip install -U yt-dlp
```

If the channel has many videos, test first:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --max-videos 3 --language es
```

## JavaScript Runtime Warning in `yt-dlp`

If you see:

```text
No supported JavaScript runtime could be found
```

it is not always fatal. If audio downloads correctly, you can continue. YouTube increasingly makes some extraction flows depend on JavaScript, so to avoid missing formats or future failures install a runtime compatible with `yt-dlp`, such as Deno or Node.js, and keep `yt-dlp` updated:

```powershell
pip install -U yt-dlp
```

---

## Español

## `yt-agent check` Dice que Whisper no Responde

Comprueba contenedores:

```powershell
docker compose ps
```

Levanta servicios:

```powershell
docker compose up -d --build
```

Si estás en Windows/Linux con NVIDIA y quieres CUDA:

```powershell
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d --build
```

Mira logs:

```powershell
docker compose logs -f whisper
```

## Whisper no Ve GPU

Esto solo aplica si arrancaste con `docker-compose.cuda.yml`. Comprueba CUDA en el host:

```powershell
nvidia-smi
```

Comprueba que Docker Desktop tenga soporte GPU activo. En WSL2/Windows, también verifica que el runtime NVIDIA esté disponible para Docker.

El healthcheck debería mostrar:

```text
GPU visible
```

## Whisper Cierra la Conexión Durante una Ingesta

Si ves algo como:

```text
RemoteDisconnected: Remote end closed connection without response
```

normalmente significa que el servicio Whisper dentro de Docker cerró la conexión durante una transcripción. Puede pasar si el contenedor se reinicia, si la GPU está ocupada, si el audio es largo o si el modelo tarda demasiado en responder.

La ingesta guarda cada transcripción completada en `data/transcripts`, así que puedes reanudar sin perder lo anterior:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es
```

Por defecto, si falla un video concreto, la ingesta continúa con el siguiente. Si prefieres que se detenga al primer error:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es --stop-on-error
```

Para procesar solo videos que no tengan transcripción cacheada:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es --skip-cached
```

Si el error se repite en videos largos, baja temporalmente el modelo Whisper. En CPU el default ya es `medium`; en CUDA puedes cambiar `WHISPER_MODEL` en `.env` a `medium` y recrear el servicio.

## La Primera Transcripción Tarda Mucho

Es normal. La primera transcripción descarga el modelo Whisper configurado en Docker Compose dentro de `data/whisper-cache`. En modo CPU se usa `medium` por defecto; en modo CUDA se usa `large-v3`.

Para usar un modelo más pequeño, cambia:

```yaml
WHISPER_MODEL: medium
```

o:

```yaml
WHISPER_MODEL: small
```

Luego recrea:

```powershell
docker compose up -d --build --force-recreate whisper
```

En modo CUDA:

```powershell
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d --build --force-recreate whisper
```

## macOS y CUDA

macOS no soporta CUDA. Usa el Compose base:

```bash
docker compose up -d --build
```

Esto ejecuta Whisper en CPU con `WHISPER_COMPUTE_TYPE=int8`. Es más lento que CUDA, pero compatible. Si necesitas acelerar transcripciones en Apple Silicon con Metal/MLX, habría que añadir un backend separado basado en `mlx-whisper`.

## Ollama no Está Instalado

Instálalo desde la página oficial:

- Windows: [ollama.com/download/windows](https://ollama.com/download/windows)
- macOS: [ollama.com/download/mac](https://ollama.com/download/mac)
- Linux: [ollama.com/download/linux](https://ollama.com/download/linux)
- Quickstart oficial: [docs.ollama.com/quickstart](https://docs.ollama.com/quickstart)

Windows PowerShell:

```powershell
irm https://ollama.com/install.ps1 | iex
```

Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Después:

```powershell
ollama list
```

Si ese comando responde, Ollama está instalado y accesible.

## Ollama no Tiene `gemma4:e2b`

```powershell
ollama pull gemma4:e2b
```

Comprueba:

```powershell
ollama list
```

## `gemma4:e2b` no Sirve Para Embeddings

Correcto. En este proyecto `gemma4:e2b` se usa como LLM. Los embeddings se hacen con SentenceTransformers por defecto.

Si quieres usar Ollama para embeddings:

```powershell
ollama pull nomic-embed-text
```

Y en `.env`:

```dotenv
EMBEDDING_PROVIDER=ollama
OLLAMA_EMBED_MODEL=nomic-embed-text
```

## Chroma no Responde

```powershell
docker compose logs -f chroma
docker compose restart chroma
```

La persistencia vive en:

```text
data/chroma/
```

## Quiero Reindexar Desde Transcripciones Existentes

Ahora mismo, relanzar la ingesta sin `--skip-cached` reutiliza transcripciones existentes y vuelve a indexar los chunks en Chroma:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es
```

## Quiero Procesar Solo Videos Nuevos

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es --skip-cached
```

## YouTube Bloquea o Limita Descargas

`yt-dlp` depende de cambios en YouTube. Actualiza dependencias:

```powershell
pip install -U yt-dlp
```

Si el canal tiene muchos videos, prueba primero:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --max-videos 3 --language es
```

## Warning de JavaScript Runtime en `yt-dlp`

Si ves:

```text
No supported JavaScript runtime could be found
```

no siempre es fatal. Si el audio se descarga correctamente, puedes continuar. YouTube está haciendo que algunos flujos de extracción dependan cada vez más de JavaScript, así que para evitar formatos ausentes o fallos futuros instala un runtime compatible con `yt-dlp`, por ejemplo Deno o Node.js, y mantén `yt-dlp` actualizado:

```powershell
pip install -U yt-dlp
```
