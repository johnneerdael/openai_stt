"""The OpenAI STT integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components import stt

from .const import DOMAIN
from .provider import OpenAISTTProvider

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenAI STT from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    provider = OpenAISTTProvider(
        hass,
        entry.data["api_key"],
        entry.data.get("model", "whisper-1"),
        entry.data.get("prompt", ""),
        entry.data.get("temperature", 0),
    )

    # Register provider directly with STT integration
    stt.async_register_stt_provider(hass, DOMAIN, provider)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unregister provider
    stt.async_unregister_stt_provider(hass, DOMAIN)
    
    # Remove data
    hass.data[DOMAIN].pop(entry.entry_id)
    
    return True 