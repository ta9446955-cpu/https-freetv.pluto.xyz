# Kodi addon README

This is a minimal Kodi plugin that loads the M3U playlist from your deployed site and displays channels as playable items.

## Installation

1. Edit `addon.xml` to set the `base_url` to your deployed Netlify site (e.g., https://your-site.netlify.app)
2. Zip the kodi-addon folder (preserve the internal folder structure) and install the addon in Kodi via "Install from zip file"

## Notes

- This addon uses the playlist provided by /api/playlist from this repository
- It expects an M3U file with #EXTINF entries followed by stream URLs
- The addon uses Python's built-in `urllib` library (no external dependencies required)
