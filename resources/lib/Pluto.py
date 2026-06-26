# -*- coding: utf-8 -*-
"""
pluto_api.py
Handles all communication with the Pluto TV API.
"""

import urllib.parse
import uuid
import requests


# API Endpoints
BOOT_URL = "https://boot.pluto.tv/v4/boot"
CHANNELS_URL = "https://service-stitcher.clusters.pluto.tv/v1/channels"
STITCH_URL = "https://service-stitcher.clusters.pluto.tv/v1/stitch/embed/hls/channel/{0}/master.m3u8"


class PlutoAPIError(Exception):
    """Custom exception for Pluto API errors."""
    pass


class PlutoClient:
    """Client for interacting with the Pluto TV API."""

    def __init__(self):
        self.session = requests.Session()
        self.client_id = str(uuid.uuid4())
        self.session_token = None
        self.server_time = None

    def _headers(self):
        """Return standard headers for Pluto API requests."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://pluto.tv",
            "Referer": "https://pluto.tv/",
        }

    def boot(self):
        """Initialize a session with Pluto TV and obtain a session token."""
        headers = self._headers()
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
        }

        try:
            resp = self.session.get(BOOT_URL, headers=headers, params=params, timeout=15)
        except requests.RequestException as e:
            raise PlutoAPIError("Could not connect to Pluto TV boot endpoint: %s" % e)

        if resp.status_code != 200:
            raise PlutoAPIError("Pluto boot failed: HTTP %s" % resp.status_code)

        body = resp.json()
        self.session_token = body.get("sessionToken")
        self.server_time = body.get("serverTime")

        if not self.session_token:
            raise PlutoAPIError("Pluto boot did not return a session token")

    def get_stream_url(self, channel_id):
        """
        Build a fresh stream URL for the given channel ID.
        This should be called at the moment of playback to ensure the JWT is fresh.
        """
        if not self.session_token:
            self.boot()

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
            "includeExtendedEvents": "true",
            "masterJWTPassthrough": "true"
        }
        if self.session_token:
            params["jwt"] = self.session_token

        # Use proper URL encoding to handle special characters in JWT
        query = urllib.parse.urlencode(params)
        return "%s?%s" % (base, query)

    def get_channels(self):
        """Fetch the list of all available live channels from Pluto TV."""
        if not self.session_token:
            self.boot()

        headers = self._headers()
        headers["Authorization"] = "Bearer %s" % self.session_token

        try:
            resp = self.session.get(CHANNELS_URL, headers=headers, timeout=15)
        except requests.RequestException as e:
            raise PlutoAPIError("Could not fetch Pluto channel list: %s" % e)

        if resp.status_code != 200:
            raise PlutoAPIError("Pluto channel list failed: HTTP %s" % resp.status_code)

        body = resp.json()
        # Handle both direct list format and wrapped data format
        raw_channels = body if isinstance(body, list) else body.get("data", [])

        channels = []
        for ch in raw_channels:
            ch_id = ch.get("id") or ch.get("_id")
            if not ch_id:
                continue

            name = ch.get("name") or "Unknown Channel"

            # Parse logo - handle both dict and string formats
            color_logo = ch.get("colorLogoPNG")
            logo = color_logo.get("path") if isinstance(color_logo, dict) else color_logo

            if not logo:  # Fallback to solid logo
                solid_logo = ch.get("solidLogoPNG")
                logo = solid_logo.get("path") if isinstance(solid_logo, dict) else solid_logo

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
        return channels
