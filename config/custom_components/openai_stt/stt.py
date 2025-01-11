"""OpenAI STT platform for speech to text."""
from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterable
from openai import OpenAI
import wave
import io

import async_timeout
import voluptuous as vol
from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    Provider,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ....custom_components.stt.const import (
    CONF_API_KEY,
    CONF_MODEL,
    CONF_PROMPT,
    CONF_TEMP,
    DEFAULT_MODEL,
    DEFAULT_PROMPT,
    DEFAULT_TEMP,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SUPPORTED_MODELS = ["whisper-1"]

SUPPORTED_LANGUAGES = [
    "af", "ar", "hy", "az", "be", "bs", "bg", "ca", "zh", "hr",
    "cs", "da", "nl", "en", "et", "fi", "fr", "gl", "de", "el",
    "he", "hi", "hu", "is", "id", "it", "ja", "kn", "kk", "ko",
    "lv", "lt", "mk", "ms", "mr", "mi", "ne", "no", "fa", "pl",
    "pt", "ro", "ru", "sr", "sk", "sl", "es", "sw", "sv", "tl",
    "ta", "th", "tr", "uk", "ur", "vi", "cy",
]

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices
) -> bool:
    """Set up OpenAI STT from a config entry."""
    provider = OpenAISTTProvider(
        hass,
        entry.data[CONF_API_KEY],
        entry.data.get(CONF_MODEL, DEFAULT_MODEL),
        entry.data.get(CONF_PROMPT, DEFAULT_PROMPT),
        entry.data.get(CONF_TEMP, DEFAULT_TEMP),
    )
    async_add_devices([provider])
    return True

class OpenAISTTProvider(Provider):
    """The OpenAI STT provider."""

    def __init__(self, hass, api_key, model, prompt, temperature) -> None:
        """Initialize OpenAI STT provider."""
        self.hass = hass
        self.name = "OpenAI STT"
        self._model = model
        self._api_key = api_key
        self._prompt = prompt
        self._temperature = temperature

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[AudioFormats]:
        """Return a list of supported formats."""
        return [AudioFormats.WAV, AudioFormats.OGG]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        """Return a list of supported codecs."""
        return [AudioCodecs.PCM, AudioCodecs.OPUS]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        """Return a list of supported bitrates."""
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        """Return a list of supported samplerates."""
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        """Return a list of supported channels."""
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> SpeechResult:
        """Process audio stream to text."""
        # Collect data
        audio_data = b""
        async for chunk in stream:
            audio_data += chunk

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
            if response.text:
                return SpeechResult(
                    response.text,
                    SpeechResultState.SUCCESS,
                )
            return SpeechResult("", SpeechResultState.ERROR) 