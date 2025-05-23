from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("xbox_game_cover_art: __init__.py loaded")

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass, config_entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = config_entry.data

    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
