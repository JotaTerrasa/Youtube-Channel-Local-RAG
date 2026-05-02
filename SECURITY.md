# Security

Este proyecto está diseñado para uso local. No expongas los servicios de Docker a internet sin autenticación y controles adicionales.

## Datos Sensibles

No publiques:

- `.env`
- audios descargados,
- transcripciones generadas,
- bases vectoriales Chroma,
- contenido privado o con copyright.

## Puertos Locales

Por defecto:

- ChromaDB: `localhost:8000`
- Whisper API: `localhost:9000`
- Ollama: `localhost:11434`

Si despliegas esto fuera de tu máquina local, añade autenticación, red privada y políticas claras de retención de datos.

