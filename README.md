# https-freetv.pluto.xyz

Pluto TV free channels site — Next.js starter for listing Pluto US channels and generating an M3U playlist.

This repository was initialized by a bot. It includes a simple Next.js app and API endpoints that read a local `channels.json` file and expose:

- /api/channels -> JSON list of channels
- /api/playlist -> M3U playlist of channels

How to use

1. Edit `channels.json` to include your working Pluto US channels. Each entry should look like:

```json
{
  "id": "pluto-1",
  "name": "Pluto Channel Name",
  "stream_url": "https://.../stream.m3u8",
  "logo": "https://.../logo.png",
  "category": "News"
}
```

2. Deploy to Vercel:
   - Go to https://vercel.com and import this repository.
   - Set the framework to "Next.js". Vercel will build and deploy automatically.

3. After deployment, visit the site root to browse channels, or use `/api/playlist` to get an M3U playlist.

Notes

- This project purposely reads a local `channels.json` file so you can maintain your curated list of working streams.
- If you want automatic fetching from Pluto's public endpoints, open an issue or request and I can add that feature.
