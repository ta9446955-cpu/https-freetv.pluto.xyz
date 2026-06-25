# -*- coding: utf-8 -*-
import uuid
import xbmc
import requests

BOOT_URL = "https://boot.pluto.tv/v4/start"
CHANNELS_URL = "https://service-channels.clusters.pluto.tv/v2/guide/channels"
STITCH_URL = "https://service-stitcher.clusters.pluto.tv/v1/stitch/embed/hls/channel/{0}/master.m3u8"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

GEO_IP = "108.82.206.181"


class PlutoAPIError(Exception):
    pass


def log(msg):
    xbmc.log("Pluto Free: %s" % msg, xbmc.LOGINFO)


class PlutoClient(object):
    def __init__(self):
        self.session = requests.Session()
        self.client_id = str(uuid.uuid4())
        self.session_token = None
        self.boot_data = None

    def _headers(self):
        return {
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Origin": "https://pluto.tv",
            "Referer": "https://pluto.tv/",
            "X-Forwarded-For": GEO_IP,
        }

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

        try:
            resp = self.session.get(BOOT_URL, headers=self._headers(), params=params, timeout=20)
        except requests.RequestException as e:
            raise PlutoAPIError("Could not reach Pluto TV (%s)" % e)

        if resp.status_code != 200:
            raise PlutoAPIError("Pluto boot failed: HTTP %s" % resp.status_code)

        try:
            data = resp.json()
        except Exception:
            raise PlutoAPIError("Pluto boot returned invalid JSON")

        self.boot_data = data
        self.session_token = data.get("sessionToken") or data.get("jwt") or data.get("token")

        if not self.session_token:
            log("boot response keys: %s" % list(data.keys()))
            raise PlutoAPIError("Pluto boot succeeded but no session token returned")

        log("boot ok, got session token (len=%d)" % len(self.session_token))
        return data

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

        try:
            resp = self.session.get(CHANNELS_URL, headers=headers, params=params, timeout=20)
        except requests.RequestException as e:
            raise PlutoAPIError("Could not fetch Pluto channel list (%s)" % e)

        if resp.status_code != 200:
            raise PlutoAPIError("Pluto channel list failed: HTTP %s" % resp.status_code)

        try:
            body = resp.json()
        except Exception:
            raise PlutoAPIError("Pluto channel list returned invalid JSON")

        raw_channels = body.get("data", [])
        channels = []

        for ch in raw_channels:
            ch_id = ch.get("id") or ch.get("_id")
            if not ch_id:
                continue

            name = ch.get("name") or ch.get("title") or "Unknown Channel"

            logo = None
            for img in ch.get("images", []) or []:
                if img.get("type") in ("colorLogoPNG", "colorLogoSVG", "logoPNG"):
                    logo = img.get("url")
                    break

            try:
                number = float(ch.get("number", 9999))
            except (TypeError, ValueError):
                number = 9999

            channels.append({
                "id": ch_id,
                "name": name,
                "number": number,
                "slug": ch.get("slug"),
                "logo": logo,
            })

        channels.sort(key=lambda c: c["number"])
        log("usable channel count after parsing: %d" % len(channels))
        return channels

    def get_stream_url(self, channel_id):
        if not self.session_token:
            self.boot()

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
            "jwt": self.session_token,
        }

        query = "&".join(
            "%s=%s" % (k, requests.utils.quote(str(v), safe=""))
            for k, v in params.items()
        )
        return "%s?%s" % (STITCH_URL.format(channel_id), query)
