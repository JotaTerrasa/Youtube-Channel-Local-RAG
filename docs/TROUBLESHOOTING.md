# Troubleshooting

## `yt-agent check` Dice que Whisper no Responde

Comprueba contenedores:

```powershell
docker compose ps
```

Levanta servicios:

```powershell
docker compose up -d --build
```

Mira logs:

```powershell
docker compose logs -f whisper
```

## Whisper no Ve GPU

Comprueba CUDA en el host:

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

Si el error se repite en videos largos, baja temporalmente el modelo Whisper en `docker-compose.yml`, por ejemplo de `large-v3` a `medium`, y recrea el servicio.

## La Primera Transcripción Tarda Mucho

Es normal. La primera transcripción descarga el modelo Whisper definido en `docker-compose.yml`, por defecto `large-v3`, dentro de `data/whisper-cache`.

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
