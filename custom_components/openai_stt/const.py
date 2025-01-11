"""Constants for OpenAI STT integration."""

DOMAIN = "openai_stt"
CONF_API_KEY = "api_key"
CONF_MODEL = "model"
CONF_PROMPT = "prompt"
CONF_TEMP = "temperature"

DEFAULT_MODEL = "whisper-1"
DEFAULT_PROMPT = ""
DEFAULT_TEMP = 0.0
DEFAULT_TIMEOUT = 10

UNIQUE_ID = "unique_id"
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB limit for Whisper 