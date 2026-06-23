# https-freetv.pluto.xyz

Pluto TV free channels site — Next.js app for listing Pluto US channels and generating an M3U playlist.

This repository includes a simple Next.js app and API endpoints that read a local `channels.json` file and expose:

- /api/channels -> JSON list of channels
- /api/playlist -> M3U playlist of channels

## How to use

1. Edit `public/channels.json` to include your working Pluto US channels. Each entry should look like:

```json
{
  "id": "pluto-1",
  "name": "Pluto Channel Name",
  "stream_url": "https://.../stream.m3u8",
  "logo": "https://.../logo.png",
  "category": "News"
}
```

2. Deploy to Netlify:
   - Go to https://netlify.com and sign in
   - Click "Add new project" → "Import an existing project"
   - Select this repository from your GitHub
   - Netlify will automatically detect Next.js and deploy
   - Your site will be live at a Netlify URL

3. After deployment, visit the site root to browse channels, or use `/api/playlist` to get an M3U playlist.

## Kodi Addon

A Kodi addon is included in the `kodi-addon/` folder that loads the M3U playlist from your deployed site and displays channels as playable items.

### Installation

1. Edit `kodi-addon/addon.xml` to set the `base_url` to your deployed Netlify site (e.g., https://your-site.netlify.app)
2. Zip the kodi-addon folder (preserve the internal folder structure) and install the addon in Kodi via "Install from zip file"

### Notes

- This addon uses the playlist provided by /api/playlist from this repository
- It expects an M3U file with #EXTINF entries followed by stream URLs
- The addon uses Python's built-in `urllib` library (no external dependencies required)

## Notes

- This project reads a local `public/channels.json` file so you can maintain your curated list of working streams
- If you want automatic fetching from Pluto's public endpoints, you can use the `/api/fetch_pluto` endpoint (best-effort, may not always work)
