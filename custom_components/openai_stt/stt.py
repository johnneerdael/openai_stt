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

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAI speech-to-text."""
    engine = OpenAISTTEngine(
        api_key=config_entry.data[CONF_API_KEY],
        model=config_entry.data.get(CONF_MODEL, DEFAULT_MODEL),
        prompt=config_entry.data.get(CONF_PROMPT, DEFAULT_PROMPT),
        temperature=config_entry.data.get(CONF_TEMP, DEFAULT_TEMP),
    )
    async_add_entities([OpenAISTTProvider(config_entry, engine)])

class OpenAISTTProvider(SpeechToTextEntity):
    """The OpenAI STT API provider."""

    def __init__(self, entry: ConfigEntry, engine: OpenAISTTEngine) -> None:
        """Initialize OpenAI STT provider."""
        self._attr_unique_id = f"{entry.entry_id}"
        self._attr_name = entry.title
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="OpenAI",
            model="Whisper",
            entry_type=dr.DeviceEntryType.SERVICE,
        )
        self._entry = entry
        self._engine = engine
        self._model = entry.data.get(CONF_MODEL, DEFAULT_MODEL)

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