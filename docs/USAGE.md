# Detailed Usage

## English

This guide assumes that you have already installed Ollama, started Docker, installed the package, and verified the environment:

```powershell
yt-agent check
```

The expected result is that Whisper responds, Chroma responds, and Ollama has `gemma4:e2b` available.

On macOS or machines without NVIDIA, Whisper runs on CPU. On Windows/Linux with NVIDIA, start the services with the CUDA override:

```powershell
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d --build
```

If you do not have Ollama, install it first from [ollama.com/download](https://ollama.com/download) and pull the model:

```powershell
ollama pull gemma4:e2b
```

## Ingest Content

### One Video

```powershell
yt-agent ingest "https://www.youtube.com/watch?v=VIDEO_ID" --language es
```

### A Playlist

```powershell
yt-agent ingest "https://www.youtube.com/playlist?list=PLAYLIST_ID" --language es
```

### A Full Channel

Use the channel `/videos` tab:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es
```

To test before processing everything:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --max-videos 3 --language es
```

### Shorts

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/shorts" --language es
```

### Only New Videos

When you have already processed a channel, update it without repeating existing transcriptions:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es --skip-cached
```

`--skip-cached` skips videos that already have a transcript in `data/transcripts`.

### Continue if One Video Fails

By default, ingestion continues when a specific video fails and marks that result as `failed`. This is useful for large channels.

If you want to stop everything on the first failure:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es --stop-on-error
```

### Recreate Transcripts

If you change the Whisper model or want to regenerate a transcript:

```powershell
yt-agent ingest "https://www.youtube.com/@CHANNEL/videos" --language es --force-transcribe
```

## Ask Questions

One-off question:

```powershell
yt-agent ask "What does the channel explain about fine-tuning?"
```

Interactive chat:

```powershell
yt-agent chat
```

Exit chat:

```text
salir
```

## How Sources Work

Each answer tries to include sources like:

```text
[1] Video title (12:31-13:48) https://www.youtube.com/watch?v=...&t=751s
```

The link opens the video at the initial timestamp of the retrieved chunk.

## Status Commands

View services:

```powershell
docker compose ps
```

View indexed chunks:

```powershell
yt-agent stats
```

View Whisper logs:

```powershell
docker compose logs -f whisper
```

View Chroma logs:

```powershell
docker compose logs -f chroma
```

## Performance

For large channels:

- Test first with `--max-videos 3`.
- Keep `--language es` if you know the language; it helps ASR.
- Use `--skip-cached` for periodic updates.
- Keep Docker and Ollama running during the full ingestion.
- Do not upload `data/` to GitHub; it can contain audio, transcripts, and large vector databases.

---

## Español

Esta guía asume que ya has instalado Ollama, levantado Docker, instalado el paquete y verificado el entorno:

```powershell
yt-agent check
```

El resultado esperado es que Whisper responda, Chroma responda y Ollama tenga disponible `gemma4:e2b`.

En macOS o máquinas sin NVIDIA, Whisper funcionará en CPU. En Windows/Linux con NVIDIA, levanta los servicios con el override CUDA:

```powershell
docker compose -f docker-compose.yml -f docker-compose.cuda.yml up -d --build
```

Si no tienes Ollama, instala primero desde [ollama.com/download](https://ollama.com/download) y descarga el modelo:

```powershell
ollama pull gemma4:e2b
```

## Ingerir Contenido

### Un Video

```powershell
yt-agent ingest "https://www.youtube.com/watch?v=VIDEO_ID" --language es
```

### Una Playlist

```powershell
yt-agent ingest "https://www.youtube.com/playlist?list=PLAYLIST_ID" --language es
```

### Un Canal Completo

Usa la pestaña `/videos` del canal:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es
```

Para probar antes de procesar todo:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --max-videos 3 --language es
```

### Shorts

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/shorts" --language es
```

### Solo Videos Nuevos

Cuando ya has procesado un canal, puedes actualizarlo sin repetir transcripciones existentes:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es --skip-cached
```

`--skip-cached` salta videos con una transcripción existente en `data/transcripts`.

### Continuar si un Video Falla

Por defecto, la ingesta continúa si falla un video concreto y marca ese resultado como `failed`. Esto es útil en canales grandes.

Si quieres detener todo al primer fallo:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es --stop-on-error
```

### Rehacer Transcripciones

Si cambias el modelo Whisper o quieres regenerar una transcripción:

```powershell
yt-agent ingest "https://www.youtube.com/@CANAL/videos" --language es --force-transcribe
```

## Preguntar

Pregunta puntual:

```powershell
yt-agent ask "Qué explica el canal sobre fine-tuning?"
```

Chat interactivo:

```powershell
yt-agent chat
```

Salir del chat:

```text
salir
```

## Cómo Funcionan las Fuentes

Cada respuesta intenta incluir fuentes como:

```text
[1] Título del video (12:31-13:48) https://www.youtube.com/watch?v=...&t=751s
```

El enlace abre el video en el timestamp inicial del chunk recuperado.

## Comandos de Estado

Ver servicios:

```powershell
docker compose ps
```

Ver chunks indexados:

```powershell
yt-agent stats
```

Ver logs de Whisper:

```powershell
docker compose logs -f whisper
```

Ver logs de Chroma:

```powershell
docker compose logs -f chroma
```

## Rendimiento

Para canales grandes:

- Prueba primero con `--max-videos 3`.
- Mantén `--language es` si sabes el idioma; ayuda al ASR.
- Usa `--skip-cached` en actualizaciones periódicas.
- Deja Docker y Ollama activos durante toda la ingesta.
- No subas `data/` a GitHub; puede contener audios, transcripciones y bases vectoriales grandes.
