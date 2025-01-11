"""The OpenAI STT integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

DOMAIN = "openai_stt"

PLATFORMS = (Platform.STT,)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up OpenAI STT from a config entry."""
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS) 