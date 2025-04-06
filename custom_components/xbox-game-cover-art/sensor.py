import logging
import aiohttp
from bs4 import BeautifulSoup

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

_LOGGER = logging.getLogger(__name__)

API_URL_TEMPLATE = "https://storeedgefd.dsx.mp.microsoft.com/v9.0/pages/pdp?market=US&locale=en-US&query={query}"
XBOX_SEARCH_URL = "https://www.xbox.com/en-us/Search?q={query}"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    entity = XboxGameCoverSensor(hass)
    async_add_entities([entity], True)


class XboxGameCoverSensor(Entity):
    def __init__(self, hass):
        self._state = None
        self._attr_name = "Xbox Game Cover"
        self._attr_icon = "mdi:microsoft-xbox"
        self.hass = hass

    @property
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        async def state_listener(event):
            await self.async_update()

        async_track_state_change_event(self.hass, "sensor.dillby777_status", state_listener)

    async def async_update(self):
        game_title_entity = self.hass.states.get("sensor.dillby777_status")
        if game_title_entity is None:
            _LOGGER.warning("sensor.dillby777_status not found")
            return

        query = game_title_entity.state.strip()
        if not query:
            _LOGGER.info("No game title to search for.")
            return

        _LOGGER.debug(f"Fetching cover for game: {query}")

        # 1. Try API method first
        try:
            api_url = API_URL_TEMPLATE.format(query=aiohttp.helpers.quote(query))
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=HEADERS, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # The data format here may change, but let's try to extract something usable
                        for item in data.get("Products", []):
                            if item.get("LocalizedProperties"):
                                images = item["LocalizedProperties"][0].get("Images", [])
                                for image in images:
                                    if image.get("ImagePurpose") == "BoxArt":
                                        self._state = image["Uri"]
                                        _LOGGER.info(f"Found box art from API: {self._state}")
                                        return
                        _LOGGER.info("No box art found in API response.")
                    else:
                        _LOGGER.warning(f"API returned status {resp.status}")
        except Exception as e:
            _LOGGER.warning(f"API call failed: {e}")

        # 2. Fallback to scraping xbox.com
        try:
            search_url = XBOX_SEARCH_URL.format(query=aiohttp.helpers.quote(query))
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=HEADERS, timeout=10) as resp:
                    text = await resp.text()
                    soup = BeautifulSoup(text, "html.parser")

                    img_tag = soup.select_one(".m-product-placement-item__img img")

                    if img_tag and "src" in img_tag.attrs:
                        self._state = img_tag["src"]
                        _LOGGER.info(f"Fallback: Found cover art via scraping: {self._state}")
                    else:
                        _LOGGER.warning("Fallback: No image found via scraping.")
                        self._state = None
        except Exception as e:
            _LOGGER.error(f"Fallback scraping failed: {e}")
            self._state = None