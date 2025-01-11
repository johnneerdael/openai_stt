"""OpenAI STT platform for speech to text."""
from __future__ import annotations

import logging
from collections.abc import AsyncIterable
import wave
import io

import async_timeout
from openai import OpenAI
from homeassistant.components import stt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

PLATFORM = "openai_stt"

SUPPORTED_LANGUAGES = [
    "af", "ar", "hy", "az", "be", "bs", "bg", "ca", "zh", "hr",
    "cs", "da", "nl", "en", "et", "fi", "fr", "gl", "de", "el",
    "he", "hi", "hu", "is", "id", "it", "ja", "kn", "kk", "ko",
    "lv", "lt", "mk", "ms", "mr", "mi", "ne", "no", "fa", "pl",
    "pt", "ro", "ru", "sr", "sk", "sl", "es", "sw", "sv", "tl",
    "ta", "th", "tr", "uk", "ur", "vi", "cy",
]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAI STT from config entry."""
    async_add_entities([OpenAISTTProvider(hass, config_entry)])

class OpenAISTTProvider(stt.SpeechToTextEntity):
    """OpenAI STT provider."""

    platform = PLATFORM

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize OpenAI STT provider."""
        self.hass = hass
        self._attr_name = "OpenAI STT"
        self._attr_unique_id = f"{config_entry.entry_id[:7]}-stt"
        self._model = config_entry.data.get("model", "whisper-1")
        self._api_key = config_entry.data["api_key"]
        self._prompt = config_entry.data.get("prompt", "")
        self._temperature = config_entry.data.get("temperature", 0)

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[stt.AudioFormats]:
        """Return a list of supported formats."""
        return [stt.AudioFormats.WAV, stt.AudioFormats.OGG]

    @property
    def supported_codecs(self) -> list[stt.AudioCodecs]:
        """Return a list of supported codecs."""
        return [stt.AudioCodecs.PCM, stt.AudioCodecs.OPUS]

    @property
    def supported_bit_rates(self) -> list[stt.AudioBitRates]:
        """Return a list of supported bitrates."""
        return [stt.AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[stt.AudioSampleRates]:
        """Return a list of supported samplerates."""
        return [stt.AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[stt.AudioChannels]:
        """Return a list of supported channels."""
        return [stt.AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: stt.SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> stt.SpeechResult:
        """Process audio stream to text."""
        _LOGGER.debug("process_audio_stream start")

        audio_data = b""
        async for chunk in stream:
            audio_data += chunk

        _LOGGER.debug(f"process_audio_stream transcribe: {len(audio_data)} bytes")

        # OpenAI client with API Key
        client = OpenAI(api_key=self._api_key)

        # convert audio data to the correct format
        wav_stream = io.BytesIO()

        with wave.open(wav_stream, 'wb') as wf:
            wf.setnchannels(metadata.channel)
            wf.setsampwidth(metadata.bit_rate // 8)
            wf.setframerate(metadata.sample_rate)
            wf.writeframes(audio_data)
        
        file = ("whisper_audio.wav", wav_stream, "audio/wav")

        def job():
            # Create transcription
            transcription = client.audio.transcriptions.create(
                model=self._model,
                language=metadata.language,
                prompt=self._prompt,
                temperature=self._temperature,
                response_format="json",
                file=file,
            )
            return transcription

        async with async_timeout.timeout(10):
            assert self.hass
            response = await self.hass.async_add_executor_job(job)
            if hasattr(response, 'text'):
                _LOGGER.info(f"process_audio_stream end: {response.text}")
                return stt.SpeechResult(
                    response.text,
                    stt.SpeechResultState.SUCCESS,
                )
            return stt.SpeechResult("", stt.SpeechResultState.ERROR) 