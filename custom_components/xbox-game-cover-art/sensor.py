import aiohttp
from homeassistant.helpers.entity import Entity
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    #_LOGGER.warning("xbox-game-cover-art: sensor async_setup_entry called")
    
    # Extract settings
    app_id = config_entry.data.get("app_id")
    api_secret = config_entry.data.get("api_secret")
    gamertags = config_entry.data.get("gamertags")

    #_LOGGER.warning("Xbox Game Cover Art - App ID: %s", app_id)
    #_LOGGER.warning("Xbox Game Cover Art - API Secret: %s", api_secret)
    #_LOGGER.warning("Xbox Game Cover Art - Gamertags: %s", gamertags)
    
    if isinstance(gamertags, str):
        gamer_ids = [gid.strip() for gid in gamertags.split(",") if gid.strip()]
    else:
        gamer_ids = gamertags or []
    
    
    entities = []
    for gamer_id in gamer_ids:
        entities.append(XboxCoverSensor(hass, gamer_id, app_id, api_secret))
        #_LOGGER.warning(f"Created XboxCoverSensor entity for gamer_id: {gamer_id}")
    
    # Example sensor to confirm it works
    async_add_entities(entities)

class XboxCoverSensor(Entity):
    def __init__(self, hass, gamer_id, app_id, api_secret):
        self.hass = hass
        self._state = f"Getting {gamer_id}   Status"
        self._attr_name = f"Xbox Cover - {gamer_id}"
        self._gamer_id = gamer_id
        self._api_ID = app_id
        self._api_S = api_secret
        self._xboxGamer = f"binary_sensor.{gamer_id}"
        self._xboxGamerInGame = f"binary_sensor.{gamer_id}_in_game"
        self._xboxGamerStatus = f"sensor.{gamer_id}_status"
        self._xboxGamerImg = None
        self._xboxGameCover = None
        self._cover_url = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iTGF5ZXJfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6Y2M9Imh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL25zIyIgdmVyc2lvbj0iMS4xIiB2aWV3Qm94PSIwIDAgMjYgMjYiPgogIDwhLS0gR2VuZXJhdG9yOiBBZG9iZSBJbGx1c3RyYXRvciAyOS40LjAsIFNWRyBFeHBvcnQgUGx1Zy1JbiAuIFNWRyBWZXJzaW9uOiAyLjEuMCBCdWlsZCAxNTIpICAtLT4KICA8cGF0aCBkPSJNMTguNSwxLjJjLTMuMS4yLTUuMSwxLjUtNS42LDEuOC0uNS0uMy0yLjQtMS42LTUuNC0xLjgsMS43LS44LDMuNS0xLjMsNS41LTEuM3MzLjguNSw1LjUsMS4yaDBaTTEyLjksOS45YzYuOCw1LjIsOC45LDkuNiw5LjUsMTItMi40LDIuNS01LjcsNC4xLTkuNCw0LjFzLTcuMi0xLjctOS42LTQuM2MuNy0yLjQsMi45LTYuNyw5LjUtMTEuOGgwWk0yMS4yLDNjMi45LDIuNCw0LjgsNS45LDQuOCwxMCwwLDIuOC0uOSw1LjQtMi40LDcuNS4zLTYuNi03LjEtMTMuOC03LjEtMTMuOC4zLTEuNSwzLTIuOCw0LjctMy42Wk00LjcsMy4xYzEuNy44LDQuMywyLjEsNC42LDMuNiwwLDAtNy4xLDctNy4xLDEzLjVDLjgsMTgsMCwxNS42LDAsMTNjMC00LDEuOC03LjUsNC43LTkuOWgwWiIgZmlsbD0iIzMzMyIvPgo8L3N2Zz4="
        self._access_token = None
        self._last_game_title = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state
        
    @property
    def entity_picture(self):
        # The cover art image that will be shown in the UI
        return self._cover_url

    @property
    def extra_state_attributes(self):
        return {
            "gamer_id": self._gamer_id,
            "xbox_Gamer": self._get_state(self._xboxGamer),
            "xbox_GamerInGame": self._get_state(self._xboxGamerInGame),
            "xbox_GamerStatus": self._get_state(self._xboxGamerStatus),
         }
         
    def _get_state(self, entity_id):
        # Get state of another HA entity (like binary_sensor.gamer_online)
        state_obj = self.hass.states.get(entity_id)
        return state_obj.state if state_obj else None
        
    async def async_update(self):
        gamer = self.hass.states.get(self._xboxGamer)
        gamergame = self.hass.states.get(self._xboxGamerInGame)
        gamerstatus = self.hass.states.get(self._xboxGamerStatus)

        self._xboxGamerImg = gamer.attributes['entity_picture']

        self._set_state()
        self._update_entity_name()
       
        if gamer.state == "on":
            if gamergame.state == "off":
                self._update_entity_picture() 
                self._last_game_title = gamerstatus.state
            if gamer.state == "on" and gamergame.state == "on":
                if self._api_ID and self._api_S and self._last_game_title != gamerstatus.state:
                    try:
                        self._access_token = await self._get_access_token()
                        game = await self._search_game(gamerstatus.state)
    
                        if game:
                            cover_url = await self._get_cover_url(game.get("cover"))
                            self._cover_url = cover_url
                            self._last_game_title = gamerstatus.state
    
                    except Exception as e:
                        self._update_entity_picture() 
                        _LOGGER.warning(f"Error updating cover art for {self._gamer_id}: {e}")
            
        else:
            self._update_entity_picture() 
            self._last_game_title = gamerstatus.state



        
    def _set_state(self):
        gamer = self.hass.states.get(self._xboxGamer)
        gamergame = self.hass.states.get(self._xboxGamerInGame)
        gamerstatus = self.hass.states.get(self._xboxGamerStatus)

        if gamer.state == "on":
            self._state = gamerstatus.state

        else:
            self._state = "Offline"
        
    def _update_entity_name(self):
        gamer = self.hass.states.get(self._xboxGamer)
        gamergame = self.hass.states.get(self._xboxGamerInGame)

        if gamer.state =="on" and gamergame.state == "on":
            self._attr_name = f"{gamer.attributes['friendly_name']} - In Game"
        else:
            self._attr_name= gamer.attributes['friendly_name']
            #_LOGGER.warning(f"friendly_name {gamer.attributes['friendly_name']}")

    async def _get_access_token(self):
        # Authenticate with Twitch to get a token for IGDB API
        async with aiohttp.ClientSession() as session:
            #_LOGGER.warning("Xbox Game Cover Art - App ID: %s", self._api_ID)
            #_LOGGER.warning("Xbox Game Cover Art - API Secret: %s", self._api_S)
            try:
                async with session.post("https://id.twitch.tv/oauth2/token",
                    params={
                        "client_id": self._api_ID,
                        "client_secret": self._api_S,
                        "grant_type": "client_credentials"
                    },
                    ) as resp:
                    data = await resp.json()
                    #_LOGGER.warning("get token data: %s", data)
                    return data["access_token"]
            except Exception as e:
                _LOGGER.error(f"Error fetching token: {e}")
                return None
                
                
    async def _search_game(self, title):
        # Search IGDB for a game by title
        async with aiohttp.ClientSession() as session:
            headers = {
                "Client-ID": self._api_ID ,
                "Authorization": f"Bearer {self._access_token}"
            }
            body = f'search "{title}"; fields name, cover; limit 1;'
            async with session.post("https://api.igdb.com/v4/games", headers=headers, data=body) as resp:
                games = await resp.json()
                return games[0] if games else None
            
    async def _get_cover_url(self, cover_id):
        # Fetch the cover image URL for a game from IGDB using the cover ID
        if not cover_id:
            return None
        async with aiohttp.ClientSession() as session:
            headers = {
                "Client-ID": self._api_ID ,
                "Authorization": f"Bearer {self._access_token}"
            }
            body = f'fields url, height, image_id; where id = {cover_id};'
            try:
                async with session.post("https://api.igdb.com/v4/covers", headers=headers, data=body) as resp:
                    covers = await resp.json()
                    #_LOGGER.warning("get covers: %s", covers)
                    if covers and isinstance(covers, list) and "url" in covers[0]:
                        raw_url = covers[0]["url"]
                        high_res_url = "https:" + raw_url.replace("t_thumb", "t_original")
                        cover_big_url = "https:" + raw_url.replace("t_thumb", "t_cover_big")
                        return high_res_url
                    return None
            except Exception as e:
                _LOGGER.error(f"Error fetching cover URL for cover ID {cover_id}: {e}")
                return None
                
    def _update_entity_picture(self):
        gamer = self.hass.states.get(self._xboxGamer)
        #_LOGGER.warning(f"gamer image {gamer.attributes['entity_picture']}")
        self._cover_url = gamer.attributes['entity_picture']