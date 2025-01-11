"""Config flow for OpenAI STT integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from openai import OpenAI, AsyncOpenAI
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
)
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
    SUPPORTED_MODELS,
    TITLE,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): TextSelector(
            TextSelectorConfig(type="password")
        ),
        vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): SelectSelector(
            SelectSelectorConfig(
                options=SUPPORTED_MODELS,
                mode="dropdown",
                translation_key="model",
            )
        ),
        vol.Optional(CONF_PROMPT, default=DEFAULT_PROMPT): TextSelector(
            TextSelectorConfig(multiline=True)
        ),
        vol.Optional(CONF_TEMP, default=DEFAULT_TEMP): NumberSelector(
            NumberSelectorConfig(
                min=0.0,
                max=1.0,
                step=0.1,
                mode="slider",
            )
        ),
    }
)

class OpenAISTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenAI STT."""

    VERSION = 1

    async def async_validate_input(self, user_input: dict[str, Any]) -> None:
        """Validate the user input allows us to connect."""
        try:
            client = AsyncOpenAI(api_key=user_input[CONF_API_KEY])
            await client.models.list()
        except Exception as ex:
            _LOGGER.error("Error validating API key: %s", str(ex))
            raise CannotConnect from ex

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self.async_validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_MODEL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{TITLE} ({user_input[CONF_MODEL]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
 