"""OpenAI STT provider implementation."""
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
    UNIQUE_ID,
)
from .engine import OpenAISTTEngine

_LOGGER = logging.getLogger(__name__)

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
    engine = OpenAISTTEngine(
        api_key=config_entry.data[CONF_API_KEY],
        model=config_entry.data.get(CONF_MODEL, DEFAULT_MODEL),
        prompt=config_entry.data.get(CONF_PROMPT, DEFAULT_PROMPT),
        temperature=config_entry.data.get(CONF_TEMP, DEFAULT_TEMP),
    )
    async_add_entities([OpenAISTTProvider(hass, config_entry, engine)])

class OpenAISTTProvider(stt.SpeechToTextEntity):
    """OpenAI STT provider."""
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, engine: OpenAISTTEngine) -> None:
        """Initialize OpenAI STT provider."""
        self.hass = hass
        self._engine = engine
        self._model = config_entry.data.get(CONF_MODEL, DEFAULT_MODEL)
        self._attr_name = f"OpenAI STT ({self._model})"
        self._attr_unique_id = config_entry.data.get(UNIQUE_ID) or f"{config_entry.entry_id}-stt"

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return self._engine.get_supported_languages()

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

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": self._attr_name,
            "model": self._model,
            "manufacturer": "OpenAI",
            "sw_version": "0.1.0",
            "entry_type": "service"
        }

    @property
    def name(self):
        """Return name of entity."""
        return self._attr_name

    async def async_process_audio_stream(
        self, metadata: stt.SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> stt.SpeechResult:
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
                    return stt.SpeechResult(response.text, stt.SpeechResultState.SUCCESS)
                return stt.SpeechResult("", stt.SpeechResultState.ERROR) 

        except MaxLengthExceeded:
            _LOGGER.error("Maximum length of the audio exceeded")
            return stt.SpeechResult("", stt.SpeechResultState.ERROR)
        except Exception as e:
            _LOGGER.error("Unknown Error: %s", e)
            return stt.SpeechResult("", stt.SpeechResultState.ERROR) 