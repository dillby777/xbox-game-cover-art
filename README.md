# Xbox Game Cover Art

A custom Home Assistant integration that shows cover art for the current Xbox game a user is playing using IGDB (Twitch) as a cover source.

![Example Screenshot](https://user-images.githubusercontent.com/YOUR_IMAGE_URL_HERE)

## Features

- Displays current Xbox game cover art for one or more Xbox Live users
- Falls back to built-in Xbox integration's `entity_picture` if a cover cannot be found on IGDB
- Uses IGDB API (requires a Twitch developer account)
- Periodically updates game art automatically

## Installation

1. **Copy Files**
   - Place this repo in `custom_components/xbox-game-cover-art` in your Home Assistant configuration directory.

2. **Install Requirements**
   - No manual pip installs required. `aiohttp` will be auto-installed based on `manifest.json`.

3. **Enable Integration**
   - Go to **Settings → Devices & Services → Add Integration** and search for "Xbox Game Cover Art".

4. **Configure**
   - Input:
     - Your **Twitch Client ID**
     - Your **Twitch Client Secret**
     - One or more Xbox Live gamer tags (comma-separated, e.g., `AGamer,BGamer`)

## Requirements

- You must have [Home Assistant's Xbox Integration](https://www.home-assistant.io/integrations/xbox/) already set up.
- You must set up a [Twitch Developer Application](https://dev.twitch.tv/console/apps) to obtain a `Client ID` and `Client Secret`.

## How It Works

- Checks whether a user is in-game using the `binary_sensor.{gamer_id}_in_game` entity.
- Gets the game title from `sensor.{gamer_id}_status`.
- Queries IGDB for the game title and retrieves the cover image.
- If the game is not recognized, it falls back to the `entity_picture` attribute from the original sensor.

## Troubleshooting

- Make sure your Xbox Live gamertag is correct.
- Verify that the Twitch Client ID and Secret are active.
- If IGDB cannot find a cover, a fallback image from the Xbox integration may appear instead.
- Check Home Assistant logs for errors (`Configuration → Logs`).

## Example Output

A sensor will be created per gamer, such as:

