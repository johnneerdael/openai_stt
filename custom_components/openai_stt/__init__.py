"""The OpenAI STT integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "openai_stt"

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up OpenAI STT from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = config_entry.data
    
    # Load stt platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "stt")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(config_entry, "stt") 