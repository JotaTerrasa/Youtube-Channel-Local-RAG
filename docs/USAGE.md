# Uso Detallado

Esta guía asume que ya has levantado Docker, instalado el paquete y verificado el entorno:

```powershell
yt-agent check
```

El resultado esperado es que Whisper vea GPU, Chroma responda y Ollama tenga disponible `gemma4:e2b`.

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

