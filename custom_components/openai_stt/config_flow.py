"""Config flow for OpenAI STT integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from openai import OpenAI

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

class OpenAISTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenAI STT integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Verify the API key works
                client = OpenAI(api_key=user_input[CONF_API_KEY])
                # Try a simple API call to validate the key
                await self.hass.async_add_executor_job(
                    lambda: client.models.list()
                )
                
                return self.async_create_entry(
                    title="OpenAI STT",
                    data=user_input
                )
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
                vol.Optional(CONF_PROMPT, default=DEFAULT_PROMPT): str,
                vol.Optional(CONF_TEMP, default=DEFAULT_TEMP): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=1)
                ),
            }),
            errors=errors,
        ) 