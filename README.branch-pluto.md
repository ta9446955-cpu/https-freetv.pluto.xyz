# https-freetv.pluto.xyz

This branch adds a simple Next.js app that serves a curated list of Pluto TV channels and provides an M3U playlist endpoint.

Files added on branch feature/pluto-addon:

- package.json, next.config.js
- pages/_app.js, pages/index.js
- pages/api/channels.js (returns JSON from public/channels.json)
- pages/api/playlist.js (returns M3U built from channels.json)
- public/channels.json (sample entries)
- styles/global.css
- vercel.json

How to use

1. Edit public/channels.json in the repository to contain working Pluto stream URLs for the channels you want to expose.
2. Push or open a Pull Request to merge feature/pluto-addon into your main branch.
3. Import the repository into Vercel (https://vercel.com) and set the framework to Next.js. Vercel will build and deploy automatically.

Endpoints

- GET /api/channels -> JSON array of channels
- GET /api/playlist -> Downloadable M3U playlist

Notes

This initial version reads a curated channels.json file in the `public/` folder. If you'd like, I can add an automatic fetcher that pulls Pluto's official catalog and normalizes stream URLs, but that requires extra maintenance.
