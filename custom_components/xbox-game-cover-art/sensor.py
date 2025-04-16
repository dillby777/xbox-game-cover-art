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
        self._cover_url = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iMjEwIiBoZWlnaHQ9IjkwIiB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6Y2M9Imh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL25zIyIgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogPG1ldGFkYXRhPgogIDxyZGY6UkRGPgogICA8Y2M6V29yayByZGY6YWJvdXQ9IiI+CiAgICA8ZGM6Zm9ybWF0PmltYWdlL3N2Zyt4bWw8L2RjOmZvcm1hdD4KICAgIDxkYzp0eXBlIHJkZjpyZXNvdXJjZT0iaHR0cDovL3B1cmwub3JnL2RjL2RjbWl0eXBlL1N0aWxsSW1hZ2UiLz4KICAgIDxkYzp0aXRsZS8+CiAgIDwvY2M6V29yaz4KICA8L3JkZjpSREY+CiA8L21ldGFkYXRhPgogPGc+CiAgPHRpdGxlPmJhY2tncm91bmQ8L3RpdGxlPgogIDxyZWN0IGlkPSJjYW52YXNfYmFja2dyb3VuZCIgeD0iLTEiIHk9Ii0xIiB3aWR0aD0iODAyIiBoZWlnaHQ9IjYwMiIgZmlsbD0ibm9uZSIvPgogPC9nPgogPGNpcmNsZSBjeD0iOTkuMTgiIGN5PSIyMCIgcj0iMTQiIGZpbGw9IiNmZmYiLz4KIDxjaXJjbGUgY3g9IjE0OC4xOCIgY3k9IjU0IiByPSIxMC41IiBmaWxsPSIjMzMzIiBzdHJva2U9IiNmZmYiLz4KIDxwYXRoIGQ9Im0xNTMuMTYgNTkuMzVjLTAuMTEgMC4yMDYtMC4zNCAwLjMyNS0wLjYyNyAwLjMyNWgtMS4zNjhjLTAuNDU1IDAtMC45ODQtMC4yODktMS4yMy0wLjY3MmwtMS43MDEtMi42NTdjLTAuMDMtMC4wNDUtMC4wNTUtMC4wNjItMC4wNjItMC4wNjQgNGUtMyAyZS0zIC0wLjAyMSAwLjAxOC0wLjA1MSAwLjA2NWwtMS43MDkgMi42NTdjLTAuMjQ3IDAuMzgzLTAuNzc2IDAuNjcxLTEuMjMgMC42NzFoLTEuMzUzYy0wLjI4OCAwLTAuNTE2LTAuMTE4LTAuNjI4LTAuMzI0LTAuMTExLTAuMjA2LTAuMDg1LTAuNDYzIDAuMDczLTAuNzAzbDIuOTc2LTQuNTQ1YTAuNzA0IDAuNzA0IDAgMCAwIDJlLTMgLTAuNjc2bC0yLjY0LTQuMDc0Yy0wLjE1NS0wLjI0MS0wLjE4LTAuNDk4LTAuMDY5LTAuNzA0IDAuMTEzLTAuMjA2IDAuMzQyLTAuMzI0IDAuNjMtMC4zMjRoMS4yODZjMC40NTcgMCAwLjk4NCAwLjI5MiAxLjIyNSAwLjY4bDEuNDkgMi4zODVhMC4yMyAwLjIzIDAgMCAwIDAuMDQ4IDAuMDU3YzNlLTMgLThlLTMgMC4wMi0wLjAyNCAwLjA0LTAuMDU3bDEuNDU1LTIuMzhjMC4yMzktMC4zOSAwLjc2NC0wLjY4NSAxLjIyMi0wLjY4NWgxLjI2N2MwLjI4NyAwIDAuNTE2IDAuMTE4IDAuNjI4IDAuMzI0IDAuMTEzIDAuMjA2IDAuMDg5IDAuNDYyLTAuMDY3IDAuNzA0bC0yLjY1OCA0LjE1YTAuNjk5IDAuNjk5IDAgMCAwIDVlLTMgMC42NzVsMi45NyA0LjQ3YzAuMTU5IDAuMjQgMC4xODcgMC40OTYgMC4wNzYgMC43MDJ6IiBmaWxsPSIjMmQ4OWVmIi8+CiA8Y2lyY2xlIGN4PSIxNjguMTgiIGN5PSI3NCIgcj0iMTAuNSIgZmlsbD0iIzMzMyIgc3Ryb2tlPSIjZmZmIi8+CiA8cGF0aCBkPSJtMTczLjU3IDc5LjM2MmMtMC4xMzQgMC4yLTAuMzY4IDAuMzE0LTAuNjQyIDAuMzE0aC0xLjExM2MtMC40OCAwLTAuOTc1LTAuMzQtMS4xNDctMC43ODlsLTAuNDktMS4yNzVhMC42NDIgMC42NDIgMCAwIDAtMC41MzItMC4zNjVoLTMuMDM2YTAuNjIgMC42MiAwIDAgMC0wLjUyIDAuMzY0bC0wLjQ2IDEuMjY3Yy0wLjE2MyAwLjQ0Ny0wLjY2MyAwLjc5OC0xLjE0IDAuNzk4aC0xLjA1M2MtMC4yNzMgMC0wLjUwOC0wLjExNS0wLjY0NC0wLjMxMy0wLjEzNi0wLjE5OS0wLjE1Ny0wLjQ1OS0wLjA1OC0wLjcxM2wzLjcxNi05LjU0YTEuMjkzIDEuMjkzIDAgMCAxIDEuMTUtMC43ODZoMS4wNDdjMC40OCAwIDAuOTc2IDAuMzM2IDEuMTU0IDAuNzgxbDMuODIgOS41NDVjMC4xMDQgMC4yNTMgMC4wODUgMC41MTMtMC4wNSAwLjcxMnptLTUuNDY3LTcuMjU3LTAuOTI2IDIuNTQyYy0wLjAyIDAuMDU1LTAuMDE4IDAuMDk1LThlLTMgMC4xMDkgMC4wMSAwLjAxMyAwLjA0NiAwLjAzIDAuMTA0IDAuMDNoMS42ODFjMC4wNjcgMCAwLjA5Ny0wLjAxOCAwLjEwMy0wLjAyOCA3ZS0zIC0wLjAxMSAwLjAxNC0wLjA0NS0wLjAxLTAuMTA3eiIgZmlsbD0iIzVkYzIxZSIvPgogPGNpcmNsZSBjeD0iMTg4LjE4IiBjeT0iNTQiIHI9IjEwLjUiIGZpbGw9IiMzMzMiIHN0cm9rZT0iI2ZmZiIvPgogPHBhdGggZD0ibTE5My41NCA1OC4xMThhMy40MiAzLjQyIDAgMCAxLTEuMTEgMS4zMThjLTAuNDY3IDAuMzI3LTEuMDQ2IDAuNTMzLTEuNzIyIDAuNjA3LTAuNDE1IDAuMDQzLTEuMzc1IDAuMDctMi44NTUgMC4wOGgtMy4yNzZjLTAuNTUxIDAtMS0wLjQ0OC0xLTF2LTEwLjI0NWMwLTAuNTUyIDAuNDQ5LTEgMS0xaDMuOTYyYzAuOTQ1IDAgMS42MzQgMC4wMzkgMi4xMDYgMC4xMTkgMC40OTYgMC4wODQgMC45NDcgMC4yNjMgMS4zNCAwLjUzIDAuMzk4IDAuMjc1IDAuNzMgMC42MzYgMC45ODYgMS4wNzQgMC4yNjcgMC40NTQgMC40MDIgMC45NjcgMC40MDIgMS41MjMgMCAwLjYwNi0wLjE2NSAxLjE2OS0wLjQ5MSAxLjY3M2EzLjA2IDMuMDYgMCAwIDEtMC42OTIgMC43NThsLTAuMDIzIDAuMDE3IDAuMDE4IDAuMDFjMC40NTQgMC4yMjQgMC44MyAwLjUyOSAxLjEyIDAuOTA1IDAuNDIyIDAuNTUzIDAuNjM3IDEuMjA3IDAuNjM3IDEuOTQ4YTMuNzkgMy43OSAwIDAgMS0wLjQwMSAxLjY4NHptLTMuNDM3LTIuODk2Yy0wLjE5NS0wLjA2OS0wLjY5NC0wLjE1LTEuOTY4LTAuMTVoLTEuMjJhMC4zNCAwLjM0IDAgMCAwLTAuMzQgMC4zNHYxLjc1OWMwIDAuMTg4IDAuMTUzIDAuMzQgMC4zNCAwLjM0aDEuNDk3YzEuMDE4IDAgMS4zOTgtMC4wMzQgMS41MzctMC4wNjMgMC4yODQtMC4wNTMgMC41MDItMC4xNyAwLjY3Mi0wLjM2IDAuMTYzLTAuMTg0IDAuMjQzLTAuNDM1IDAuMjQzLTAuNzYzIDAtMC4yODMtMC4wNjMtMC41MS0wLjE5My0wLjY5OWExLjEwNyAxLjEwNyAwIDAgMC0wLjU2OC0wLjQwNHptLTMuMTg4LTIuNzM4aDAuODY1YzAuODk1IDAgMS40NTQtMC4wMTMgMS42NjEtMC4wMzcgMC4zMjItMC4wMzggMC41NzQtMC4xNDcgMC43NDktMC4zMiAwLjE2Ni0wLjE2NyAwLjI0Ny0wLjM4NyAwLjI0Ny0wLjY3MiAwLTAuMTM2LTAuMDE3LTAuMjYtMC4wNTItMC4zNjctMC4wNTEtMC4xNi0wLjI5LTAuNDIyLTAuNDQ3LTAuNDg4LTAuMTEtMC4wNDctMC4yNC0wLjA4LTAuMzktMC4wOTgtMC4yMTMtMC4wMjUtMC44NzMtMC4wMzctMS45NTgtMC4wMzdoLTAuNjc0YTAuMzQgMC4zNCAwIDAgMC0wLjM0IDAuMzR2MS4zMzljMCAwLjE4OCAwLjE1MiAwLjM0IDAuMzQgMC4zNHoiIGZpbGw9IiNlMTEiLz4KIDxjaXJjbGUgY3g9IjE2OC4xOCIgY3k9IjM0IiByPSIxMC41IiBmaWxsPSIjMzMzIiBzdHJva2U9IiNmZmYiLz4KIDxwYXRoIGQ9Im0xNzMuMTMgMjkuMzUzLTMuMjY5IDUuMTZjLTAuMTQ5IDAuMjM2LTAuMjggMC42ODctMC4yOCAwLjk2NXYzLjI0OWEwLjk1IDAuOTUgMCAwIDEtMC45NDggMC45NDhoLTAuOTE2YTAuOTUgMC45NSAwIDAgMS0wLjk0OS0wLjk0OHYtMy4yNjRjMC0wLjI3OS0wLjEzLTAuNzI5LTAuMjgtMC45NjRsLTMuMjU0LTUuMTQ2Yy0wLjE1Mi0wLjI0My0wLjE3Ni0wLjUtMC4wNjItMC43MDUgMC4xMTMtMC4yMDUgMC4zNDMtMC4zMjMgMC42MjktMC4zMjNoMS4yOTNjMC40NiAwIDAuOTgzIDAuMjk3IDEuMjE5IDAuNjkybDEuODgzIDMuMTY3YzAuMDEzIDAuMDIgMC4wMjMgMC4wMzUgMC4wMzMgMC4wNDUgNGUtMyAtMC4wMSAwLjAxMy0wLjAyNCAwLjAyNS0wLjA0NGwxLjg0NC0zLjE2M2MwLjIzMi0wLjM5OCAwLjc1NC0wLjY5NyAxLjIxNS0wLjY5N2gxLjI1MmMwLjI4NyAwIDAuNTE2IDAuMTE4IDAuNjI5IDAuMzI0IDAuMTE0IDAuMjA1IDAuMDkgMC40NjItMC4wNjQgMC43MDR6IiBmaWxsPSIjZmZjNDBkIi8+CiA8ZyBmaWxsPSIjMzMzIj4KICA8cGF0aCBkPSJtMzYuMzk3IDQ2LjY5YzAgMC42MDQgMC40OSAxLjA5NCAxLjA5MyAxLjA5NGgxMi4xOXYxMi40MzJoLTEyLjE5Yy0wLjYwMyAwLTEuMDkzIDAuNDktMS4wOTMgMS4wOTN2MTIuMTkxaC0xMi40MzR2LTEyLjE5YzAtMC42MDQtMC40OS0xLjA5NC0xLjA5My0xLjA5NGgtMTIuMTl2LTEyLjQzMmgxMi4xOWMwLjYwMyAwIDEuMDkzLTAuNDkgMS4wOTMtMS4wOTN2LTEyLjE5MWgxMi40MzR6IiBzdHJva2U9IiNmZmYiLz4KICA8cGF0aCBkPSJtMTA0LjY0IDguMjQ1Yy0zLjA3NSAwLjE4NC01LjA5OCAxLjQ5OC01LjU4OCAxLjg0OC0wLjQ3My0wLjM0My0yLjQyNS0xLjU5Ny01LjM4My0xLjgyNSAxLjY3OC0wLjc5MiAzLjUzMi0xLjI2OCA1LjUwOC0xLjI2OCAxLjk2IDAgMy43OTcgMC40NjYgNS40NjQgMS4yNDV6bS01LjU4NyA4LjdjNi43ODggNS4yNDIgOC44ODggOS42MjIgOS41MzUgMTEuOTczLTIuMzcxIDIuNTAzLTUuNzAyIDQuMDgyLTkuNDEyIDQuMDgyLTMuODEzIDAtNy4yMTQtMS42OC05LjU5NS00LjMwMyAwLjcxOC0yLjQwMiAyLjg5MS02LjY3MSA5LjQ3Mi0xMS43NTN6bTguMzYxLTYuOTJjMi44ODQgMi4zODggNC43NjIgNS45NDcgNC43NjMgOS45NzUgMCAyLjc5Ny0wLjkwOSA1LjM3Ni0yLjQxOCA3LjQ5OSAwLjMyNS02LjYzNy03LjA2Ny0xMy44MzgtNy4wNjctMTMuODM4IDAuMjY4LTEuNDc2IDIuOTc4LTIuODA3IDQuNzIyLTMuNjM2em0tMTYuNTY1IDAuMDc3YzEuNzQ0IDAuODMyIDQuMzA3IDIuMTM0IDQuNTY4IDMuNTY1IDAgMC03LjEzMyA2Ljk1Ni03LjA3MyAxMy40OTdhMTIuOTI2IDEyLjkyNiAwIDAgMS0yLjE2Ny03LjE2MWMwLTMuOTg3IDEuODM4LTcuNTE2IDQuNjcyLTkuOXoiLz4KICA8cGF0aCBkPSJtOTkuNzYxIDY1LjIzMmgtMS41MzY0djcuNjgyMmgxLjUzNjR2LTcuNjgyMm0zLjcxMDUgMS42NjctMS4wOTA5IDEuMDkwOWMxLjI1OTkgMS4wMTQgMS45ODk3IDIuNTQyOCAxLjk4OTcgNC4xNTYxYTUuMzc3NSA1LjM3NzUgMCAwIDEtNS4zNzc1IDUuMzc3NWMtMi45NjUzIDAtNS4zNzc1LTIuMzk2OC01LjM3NzUtNS4zNzc1IDAtMS42MDU2IDAuNzI5ODEtMy4xNDIgMS45ODItNC4xNjM3bC0xLjA4MzItMS4wODMyYy0yLjkxMTUgMi40NzM3LTMuMjY0OSA2LjgzNzEtMC43OTEyNiA5Ljc0ODcgMi40NzM3IDIuOTAzOSA2LjgzNzEgMy4yNTcyIDkuNzQ4NyAwLjc4MzU4IDEuNTUxOC0xLjMxMzYgMi40MzUyLTMuMjQ5NiAyLjQzNTItNS4yODUzIDAtMi4wMjA0LTAuODkxMTMtMy45NDEtMi40MzUyLTUuMjQ2OXoiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9Ii43NjgyMiIgc3R5bGU9InBhaW50LW9yZGVyOnN0cm9rZSBmaWxsIG1hcmtlcnMiLz4KIDwvZz4KPC9zdmc+Cg=="
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