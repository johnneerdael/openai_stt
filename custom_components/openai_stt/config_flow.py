"""Config flow for OpenAI STT integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from openai import OpenAI
from homeassistant.helpers.selector import selector
from homeassistant.exceptions import HomeAssistantError
import logging
from typing import Any

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

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
        vol.Optional(CONF_PROMPT, default=DEFAULT_PROMPT): str,
        vol.Optional(CONF_TEMP, default=DEFAULT_TEMP): float,
    }
)

class OpenAISTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenAI STT."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            # Test API key
            client = OpenAI(api_key=user_input[CONF_API_KEY])
            models = client.models.list()
            if not any(model.id == user_input[CONF_MODEL] for model in models):
                errors["base"] = "invalid_model"
        except Exception:  # pylint: disable=broad-except
            errors["base"] = "cannot_connect"
        else:
            await self.async_set_unique_id(user_input[CONF_MODEL])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"OpenAI STT ({user_input[CONF_MODEL]})",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
 