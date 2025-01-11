"""The OpenAI STT integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MODEL,
    CONF_PROMPT,
    CONF_TEMP,
    DEFAULT_MODEL,
    DEFAULT_PROMPT,
    DEFAULT_TEMP,
)

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): cv.string,
    vol.Optional(CONF_PROMPT, default=DEFAULT_PROMPT): cv.string,
    vol.Optional(CONF_TEMP, default=DEFAULT_TEMP): vol.All(
        vol.Coerce(float), vol.Range(min=0, max=1)
    ),
})

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the OpenAI STT component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up OpenAI STT from a config entry."""
    return True 