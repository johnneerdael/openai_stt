"""Constants for the OpenAI Speech-to-Text integration."""
import logging

_LOGGER = logging.getLogger(__package__)

DOMAIN = "openai_stt"
DEFAULT_MODEL = "whisper-1"
DEFAULT_PROMPT = ""
DEFAULT_TEMP = 0.0
DEFAULT_TIMEOUT = 30
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB

CONF_API_KEY = "api_key"
CONF_MODEL = "model"
CONF_PROMPT = "prompt"
CONF_TEMP = "temperature"

SUPPORTED_MODELS = [
    "whisper-1",
] 