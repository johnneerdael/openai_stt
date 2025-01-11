"""The OpenAI STT integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .provider import OpenAISTTProvider

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenAI STT from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    provider = OpenAISTTProvider(
        hass,
        entry.data["api_key"],
        entry.data.get("model", "whisper-1"),
        entry.data.get("prompt", ""),
        entry.data.get("temperature", 0),
    )

    # Store provider instance in hass.data
    hass.data[DOMAIN][entry.entry_id] = provider

    # Register provider with STT
    hass.config_entries.async_register_platform(entry, "stt", provider)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if provider := hass.data[DOMAIN].pop(entry.entry_id, None):
        # Unregister provider from STT
        hass.config_entries.async_unregister_platform(entry, "stt", provider)
    return True 