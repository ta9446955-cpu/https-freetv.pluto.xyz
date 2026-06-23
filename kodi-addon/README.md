# Kodi addon README

This is a minimal Kodi plugin that loads the M3U playlist from your deployed site and displays channels as playable items.

Installation

1. Edit the addon settings (or edit addon.xml default) to set `base_url` to your deployed site (e.g., https://your-deploy.vercel.app).
2. Zip the kodi-addon folder (preserve the internal folder structure) and install the addon in Kodi via "Install from zip file".

Notes

- This addon is intentionally minimal and uses the playlist provided by /api/playlist from this repository. It expects an M3U file with #EXTINF entries followed by stream URLs.
- Kodi's Python environment may not include the `requests` library. If not available, you will need to vendor a simple HTTP fetch or use Kodi's built-in `urllib`.
