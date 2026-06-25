# -*- coding: utf-8 -*-
"""
pluto_api.py
Updated Pluto TV client for cfd-v4 stitcher (2026)
"""

import uuid
import json

import xbmc
# Use urllib instead of requests (Kodi doesn't include requests by default)
try:
    import urllib.request as urllib_request
    import urllib.parse as urllib_parse
    import urllib.error as urllib_error
except ImportError:
    import urllib2 as urllib_request
    import urllib as urllib_parse
    import urllib2 as urllib_error


BOOT_URL = "https://boot.pluto.tv/v4/start"
CHANNELS_URL = "https://service-channels.clusters.pluto.tv/v2/guide/channels"

# New cfd-v4 stitcher endpoint
STITCH_URL = "https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/stitch/hls/channel/{0}/master.m3u8"

# Fallback old endpoint (if cfd-v4 fails in your region)
# STITCH_URL = "https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/{0}/master.m3u8"


def log(msg):
    xbmc.log("Pluto Free: %s" % msg, xbmc.LOGINFO)


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# US-based IP for geo-gating
GEO_IP = "108.82.206.181"


class PlutoAPIError(Exception):
    pass


class PlutoClient(object):
    def __init__(self):
        self.client_id = str(uuid.uuid4())
        self.session_token = None

    def _headers(self):
        return {
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Origin": "https://pluto.tv",
            "Referer": "https://pluto.tv/",
            "X-Forwarded-For": GEO_IP,
        }

    def _get(self, url, params=None, headers=None):
        """Make a GET request using urllib (no requests dependency)."""
        if params:
            query = urllib_parse.urlencode(params)
            url = "%s?%s" % (url, query)
        
        req = urllib_request.Request(url, headers=headers or self._headers())
        
        try:
            resp = urllib_request.urlopen(req, timeout=15)
        except urllib_error.HTTPError as e:
            raise PlutoAPIError("HTTP %s: %s" % (e.code, e.reason))
        except urllib_error.URLError as e:
            raise PlutoAPIError("Could not reach Pluto TV (%s)" % e.reason)
        
        return json.loads(resp.read().decode('utf-8'))

    def boot(self):
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
        
        data = self._get(BOOT_URL, params=params)
        
        token = data.get("sessionToken")
        if not token:
            log("boot response keys: %s" % list(data.keys()))
            raise PlutoAPIError("Pluto boot succeeded but no session token returned")

        log("boot ok, got session token (len=%d)" % len(token))
        self.session_token = token
        return token

    def get_channels(self):
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
        
        body = self._get(CHANNELS_URL, params=params, headers=headers)
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
        base = STITCH_URL.format(channel_id)
        params = {
            "terminate": "false",
            "deviceType": "web",
            "deviceMake": "web",
            "deviceModel": "web",
            "deviceVersion": "DNT",
            "appVersion": "DNT",
            "deviceDNT": "1",
            "sid": self.client_id,
            "deviceId": channel_id,
            "userId": "",
            "advertisingId": "",
            "deviceLat": "",
            "deviceLon": "",
            "app_name": "",
            "appName": "web",
            "buildVersion": "",
            "appStoreUrl": "",
            "architecture": "",
            "includeExtendedEvents": "false",
            "serverSideAds": "false",
            "marketingRegion": "US",
        }
        if self.session_token:
            params["jwt"] = self.session_token
        
        query = urllib_parse.urlencode(params)
        return "%s?%s" % (base, query)
