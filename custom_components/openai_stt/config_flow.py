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
    UNIQUE_ID,
)

_LOGGER = logging.getLogger(__name__)

def generate_unique_id(user_input: dict) -> str:
    """Generate a unique id from user input."""
    model = user_input[CONF_MODEL]
    prompt = user_input.get(CONF_PROMPT, "")
    temp = str(user_input.get(CONF_TEMP, DEFAULT_TEMP))
    return f"{model}_{prompt}_{temp}"

async def validate_user_input(user_input: dict):
    """Validate user input fields."""
    if user_input.get(CONF_MODEL) is None:
        raise ValueError("Model is required")
    if not isinstance(user_input.get(CONF_TEMP, DEFAULT_TEMP), (int, float)):
        raise ValueError("Temperature must be a number between 0 and 1")

class OpenAISTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenAI STT integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                # Validate input
                await validate_user_input(user_input)
                
                # Verify the API key works
                client = OpenAI(api_key=user_input[CONF_API_KEY])
                try:
                    await self.hass.async_add_executor_job(
                        lambda: client.models.list()
                    )
                except Exception as err:
                    _LOGGER.error("Failed to validate API key: %s", str(err))
                    raise InvalidAuth from err
                    
                # Generate unique_id
                unique_id = generate_unique_id(user_input)
                user_input[UNIQUE_ID] = unique_id
                
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"OpenAI STT ({user_input[CONF_MODEL]})",
                    data=user_input
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except ValueError as err:
                _LOGGER.error("Validation error: %s", str(err))
                errors["base"] = str(err)
            except Exception as err:
                _LOGGER.exception("Unexpected exception: %s", str(err))
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_MODEL, default=DEFAULT_MODEL): selector({
                "select": {
                    "options": ["whisper-1"],
                    "mode": "dropdown",
                    "sort": True,
                    "custom_value": True
                }
            }),
            vol.Optional(CONF_PROMPT, default=DEFAULT_PROMPT): str,
            vol.Optional(CONF_TEMP, default=DEFAULT_TEMP): vol.All(
                vol.Coerce(float), vol.Range(min=0, max=1)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        ) 

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
 