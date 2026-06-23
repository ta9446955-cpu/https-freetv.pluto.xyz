### Automatic Pluto catalog fetcher

I added a serverless API at `/api/fetch_pluto` that will attempt to fetch a Pluto channel catalog from one of several candidate endpoints.

How it works

- The endpoint will try these sources (in order):
  - The environment variable `PLUTO_CATALOG_URL` (set this in Vercel to point to a working Pluto catalog JSON).
  - A couple of public Pluto-like endpoints (best-effort).
- The response is a normalized JSON object: `{ source: 'url', channels: [ {id,name,logo,category,stream_url} ] }`.

Why this is best-effort

- Pluto's public APIs and stream URLs are not officially documented for broad redistribution, and upstream fields may change. The fetcher will return whatever it can find and normalize fields when possible.

How to use

- If you have a reliable Pluto catalog URL, set the `PLUTO_CATALOG_URL` environment variable in Vercel to point to it. The site will then be able to use the remote catalog.
- If no external catalog is available, the site will fall back to `public/channels.json`.

Example: in Vercel project settings add `PLUTO_CATALOG_URL` = `https://example.com/pluto-catalog.json`
