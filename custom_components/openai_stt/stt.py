"""Support for the OpenAI speech to text service."""
from __future__ import annotations

import logging
from collections.abc import AsyncIterable
import wave
import io

import async_timeout
from openai import OpenAI
from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
    SpeechToTextEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import MaxLengthExceeded

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MODEL,
    CONF_PROMPT,
    CONF_TEMP,
    DEFAULT_MODEL,
    DEFAULT_PROMPT,
    DEFAULT_TEMP,
    DEFAULT_TIMEOUT,
    MAX_AUDIO_SIZE,
)

_LOGGER = logging.getLogger(__name__)

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

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAI STT platform from a config entry."""
    api_key = config_entry.data[CONF_API_KEY]
    model = config_entry.data.get(CONF_MODEL, DEFAULT_MODEL)
    prompt = config_entry.data.get(CONF_PROMPT, DEFAULT_PROMPT)
    temperature = config_entry.data.get(CONF_TEMP, DEFAULT_TEMP)

    engine = OpenAISTTEngine(api_key, model, prompt, temperature)
    
    async_add_entities(
        [
            OpenAISTTProvider(
                hass,
                config_entry.entry_id,
                engine,
                config_entry.title,
            )
        ]
    )

class OpenAISTTProvider(SpeechToTextEntity):
    """OpenAI STT provider."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        engine: OpenAISTTEngine,
        name: str,
    ) -> None:
        """Initialize OpenAI STT provider."""
        self.hass = hass
        self._attr_unique_id = f"{entry_id}_stt"
        self._attr_name = name
        self._engine = engine

        self._attr_supported_languages = ["*"]
        self._attr_supported_formats = [AudioFormats.WAV]
        self._attr_supported_codecs = [AudioCodecs.PCM]
        self._attr_supported_bit_rates = [AudioBitRates.BITRATE_16]
        self._attr_supported_sample_rates = [
            AudioSampleRates.SAMPLERATE_16000,
            AudioSampleRates.SAMPLERATE_44100,
        ]
        self._attr_supported_channels = [
            AudioChannels.CHANNEL_MONO,
            AudioChannels.CHANNEL_STEREO,
        ]

    @property
    def device_info(self) -> dr.DeviceInfo:
        """Return device information about OpenAI STT."""
        return dr.DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self.name,
            manufacturer="OpenAI",
            model=self._engine._model,
        )

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return self._engine.get_supported_languages()

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
        _LOGGER.debug("Process audio stream start")

        audio_data = b""
        async for chunk in stream:
            audio_data += chunk

        _LOGGER.debug(f"Process audio stream transcribe: {len(audio_data)} bytes")

        # convert audio data to the correct format
        wav_stream = io.BytesIO()

        with wave.open(wav_stream, 'wb') as wf:
            wf.setnchannels(metadata.channel)
            wf.setsampwidth(metadata.bit_rate // 8)
            wf.setframerate(metadata.sample_rate)
            wf.writeframes(audio_data)
        
        file = ("whisper_audio.wav", wav_stream, "audio/wav")

        try:
            if len(audio_data) > MAX_AUDIO_SIZE:
                raise MaxLengthExceeded
                
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                assert self.hass
                response = await self.hass.async_add_executor_job(
                    lambda: self._engine.transcribe(file, metadata.language)
                )
                if hasattr(response, 'text'):
                    _LOGGER.info(f"Process audio stream end: {response.text}")
                    return SpeechResult(response.text, SpeechResultState.SUCCESS)
                return SpeechResult("", SpeechResultState.ERROR) 

        except MaxLengthExceeded:
            _LOGGER.error("Maximum length of the audio exceeded")
            return SpeechResult("", SpeechResultState.ERROR)
        except Exception as e:
            _LOGGER.error("Unknown Error: %s", e)
            return SpeechResult("", SpeechResultState.ERROR) 