# -*- coding: utf-8 -*-
"""
pluto_api.py
Lightweight client for Pluto TV's public web API.
Mirrors the same calls Pluto's own web player (pluto.tv) makes:
  1. GET boot.pluto.tv/v4/start      -> session token + base ad-stitch params
  2. GET service-channels.clusters.pluto.tv/v2/guide/channels -> channel list
  3. Stream URL for each channel is built directly from the channel id via
     Pluto's stitcher service.

No login/account credentials are required for the free, ad-supported
live channel lineup -- this is the same flow the pluto.tv website uses
for anonymous/guest viewing.
"""

import uuid
import xbmc
import requests

BOOT_URL = "https://boot.pluto.tv/v4/start"
CHANNELS_URL = "https://service-channels.clusters.pluto.tv/v2/guide/channels"
STITCH_URL = "https://service-stitcher.clusters.pluto.tv/v1/stitch/embed/hls/channel/{0}/master.m3u8"


def log(msg):
    xbmc.log("Pluto Free: %s" % msg, xbmc.LOGINFO)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# A US-based IP to use for X-Forwarded-For. Pluto's free guide/channel
# data is geo-gated; without a recognized region signal, some endpoints
# return HTTP 200 with an empty channel list instead of an error.
GEO_IP = "108.82.206.181"  # us_east, known-good per community tooling


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
            "X-Forwarded-For": GEO_IP,
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
            log("boot response keys: %s" % list(data.keys()))
            raise PlutoAPIError("Pluto boot succeeded but no session token returned")

        log("boot ok, got session token (len=%d)" % len(token))
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
            log("channels HTTP %s body=%s" % (resp.status_code, resp.text[:500]))
            raise PlutoAPIError("Pluto channel list failed: HTTP %s" % resp.status_code)

        body = resp.json()
        raw_channels = body.get("data", [])
        log("raw channel count from API: %d" % len(raw_channels))

        if raw_channels:
            log("sample channel keys: %s" % list(raw_channels[0].keys()))
        else:
            log("EMPTY data field. Full response body: %s" % str(body)[:1500])

        channels = []
        for ch in raw_channels:
            ch_id = ch.get("id") or ch.get("_id")
            if not ch_id:
                continue

            name = ch.get("name") or ch.get("title") or "Unknown Channel"

            logo = None
            for img in ch.get("images", []) or []:
                if img.get("type") == "colorLogoPNG":
                    logo = img.get("url")
                    break

            try:
                number = float(ch.get("number", 9999))
            except (TypeError, ValueError):
                number = 9999

            stream_url = self._build_stream_url(ch_id)

            channels.append({
                "id": ch_id,
                "name": name,
                "number": number,
                "slug": ch.get("slug"),
                "logo": logo,
                "stream_url": stream_url,
            })

        log("usable channel count after parsing: %d" % len(channels))
        channels.sort(key=lambda c: c["number"])
        return channels

    def _build_stream_url(self, channel_id):
        """Build the HLS stitcher URL directly from the channel id. This is
        the same endpoint shape Pluto's own clients use for live channel
        playback, independent of whatever extra metadata fields the guide
        response does or doesn't include."""
        base = STITCH_URL.format(channel_id)
        params = {
            "deviceType": "web",
            "deviceMake": "chrome",
            "deviceModel": "web",
            "deviceVersion": "124.0.0",
            "appName": "web",
            "appVersion": "9.0.0",
            "clientID": self.client_id,
            "clientModelNumber": "1.0.0",
            "serverSideAds": "false",
            "sid": self.client_id,
        }
        if self.session_token:
            params["jwt"] = self.session_token
        query = "&".join("%s=%s" % (k, v) for k, v in params.items())
        return "%s?%s" % (base, query)
