"""OpenAI STT engine implementation."""
from openai import OpenAI

class OpenAISTTEngine:
    """OpenAI STT engine."""

    def __init__(self, api_key: str, model: str, prompt: str, temperature: float):
        """Initialize OpenAI STT engine."""
        self._api_key = api_key
        self._model = model
        self._prompt = prompt
        self._temperature = temperature

    def transcribe(self, audio_file: tuple, language: str | None = None):
        """Transcribe audio using OpenAI API."""
        client = OpenAI(api_key=self._api_key)
        return client.audio.transcriptions.create(
            model=self._model,
            language=language,
            prompt=self._prompt,
            temperature=self._temperature,
            response_format="json",
            file=audio_file,
        )

    @staticmethod
    def get_supported_languages() -> list[str]:
        """Return list of supported languages."""
        return ["af", "ar", "hy", "az", "be", "bs", "bg", "ca", "zh", "hr",
                "cs", "da", "nl", "en", "et", "fi", "fr", "gl", "de", "el",
                "he", "hi", "hu", "is", "id", "it", "ja", "kn", "kk", "ko",
                "lv", "lt", "mk", "ms", "mr", "mi", "ne", "no", "fa", "pl",
                "pt", "ro", "ru", "sr", "sk", "sl", "es", "sw", "sv", "tl",
                "ta", "th", "tr", "uk", "ur", "vi", "cy"] 