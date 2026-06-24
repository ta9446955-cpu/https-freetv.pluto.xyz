# -*- coding: utf-8 -*-
"""
pluto_api.py
Lightweight client for Pluto TV's public web API.
Mirrors the same calls Pluto's own web player (pluto.tv) makes:
  1. GET boot.pluto.tv/v4/start      -> session token + base ad-stitch params
  2. GET service-channels.clusters.pluto.tv/v2/guide/channels -> channel list
  3. Stream URL for each channel is built from Pluto's stitcher service,
     using the session token obtained in step 1.

No login/account credentials are required for the free, ad-supported
live channel lineup -- this is the same flow the pluto.tv website uses
for anonymous/guest viewing.
"""

import uuid
import requests

BOOT_URL = "https://boot.pluto.tv/v4/start"
CHANNELS_URL = "https://service-channels.clusters.pluto.tv/v2/guide/channels"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class PlutoAPIError(Exception):
    pass


class PlutoClient(object):
    def __init__(self):
        self.session = requests.Session()
        self.client_id = str(uuid.uuid4())
        self.session_token = None
        self.stitcher_params = None

    def _headers(self):
        return {
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Origin": "https://pluto.tv",
            "Referer": "https://pluto.tv/",
        }

    def boot(self):
        """Start a Pluto session and store the bearer token used by
        every subsequent request (channel list + stream playback)."""
        params = {
            "appName": "web",
            "appVersion": "9.0.0",
            "deviceVersion": "124.0.0",
            "deviceModel": "web",
            "deviceMake": "chrome",
            "deviceType": "web",
            "clientID": self.client_id,
            "clientModelNumber": "1.0.0",
            "serverSideAds": "false",
            "drmCapabilities": "widevine:L3",
        }
        try:
            resp = self.session.get(BOOT_URL, headers=self._headers(), params=params, timeout=15)
        except requests.RequestException as e:
            raise PlutoAPIError("Could not reach Pluto TV (%s)" % e)

        if resp.status_code != 200:
            raise PlutoAPIError("Pluto boot failed: HTTP %s" % resp.status_code)

        data = resp.json()
        token = data.get("sessionToken")
        if not token:
            raise PlutoAPIError("Pluto boot succeeded but no session token returned")

        self.session_token = token
        return token

    def get_channels(self):
        """Return a list of dicts: id, name, logo, slug, number, stream_url."""
        if not self.session_token:
            self.boot()

        headers = self._headers()
        headers["Authorization"] = "Bearer %s" % self.session_token

        params = {
            "channelIds": "",
            "offset": "0",
            "limit": "1000",
            "sort": "number:asc",
        }
        try:
            resp = self.session.get(CHANNELS_URL, headers=headers, params=params, timeout=15)
        except requests.RequestException as e:
            raise PlutoAPIError("Could not fetch Pluto channel list (%s)" % e)

        if resp.status_code != 200:
            raise PlutoAPIError("Pluto channel list failed: HTTP %s" % resp.status_code)

        raw_channels = resp.json().get("data", [])

        channels = []
        for ch in raw_channels:
            stitched = ch.get("stitched") or {}
            paths = stitched.get("paths") or []
            stream_path = None
            for p in paths:
                if p.get("type") == "hls":
                    stream_path = p.get("path")
                    break
            if not stream_path:
                # fall back to first available path if "hls" not explicitly tagged
                if paths:
                    stream_path = paths[0].get("path")
                else:
                    continue

            logo = None
            for img in ch.get("images", []):
                if img.get("type") == "colorLogoPNG":
                    logo = img.get("url")
                    break

            stream_url = self._build_stream_url(stream_path)

            channels.append({
                "id": ch.get("id"),
                "name": ch.get("name", "Unknown Channel"),
                "number": ch.get("number", 9999),
                "slug": ch.get("slug"),
                "logo": logo,
                "stream_url": stream_url,
            })

        channels.sort(key=lambda c: c["number"])
        return channels

    def _build_stream_url(self, stream_path):
        """Pluto serves HLS through stitcher.pluto.tv. The stitched path
        already contains the playback id; we just need to attach the
        session/client identifiers so the edge will authorize playback."""
        base = "https://stitcher.pluto.tv" + stream_path
        sep = "&" if "?" in base else "?"
        return (
            "%s%ssessionToken=%s&clientID=%s&deviceType=web&deviceMake=chrome"
            "&appName=web&appVersion=9.0.0"
            % (base, sep, self.session_token, self.client_id)
        )
