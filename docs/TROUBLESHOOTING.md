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
