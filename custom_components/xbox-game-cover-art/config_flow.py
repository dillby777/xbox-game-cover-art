from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN, CONF_APP_ID, CONF_API_SECRET, CONF_GAMERTAGS

class XboxGameCoverArtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Xbox Game Cover Art", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_APP_ID): str,
                vol.Required(CONF_API_SECRET): str,
                vol.Required(CONF_GAMERTAGS): str,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        # Reintroduce the config_entry parameter and pass it to the handler
        return XboxGameCoverArtOptionsFlowHandler(config_entry)


class XboxGameCoverArtOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Update the configuration entry with the new values
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, **user_input}
            )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_APP_ID, default=self.config_entry.data.get(CONF_APP_ID, "")): str,
                vol.Required(CONF_API_SECRET, default=self.config_entry.data.get(CONF_API_SECRET, "")): str,
                vol.Required(CONF_GAMERTAGS, default=self.config_entry.data.get(CONF_GAMERTAGS, "")): str,
            })
        )
