def _build_stream_url(self, channel_id):
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
        "includeExtendedEvents": "true",      # Required for v2
        "masterJWTPassthrough": "true"        # Required for v2
    }
    if self.session_token:
        params["jwt"] = self.session_token    # JWT must be in the URL params
        
    query = "&".join("%s=%s" % (k, v) for k, v in params.items())
    return "%s?%s" % (base, query)def get_channels(self):
    if not self.session_token:
        self.boot()

    headers = self._headers()
    headers["Authorization"] = "Bearer %s" % self.session_token

    try:
        # No params needed, this endpoint returns all channels by default
        resp = self.session.get(CHANNELS_URL, headers=headers, timeout=15)
    except requests.RequestException as e:
        raise PlutoAPIError("Could not fetch Pluto channel list (%s)" % e)

    if resp.status_code != 200:
        raise PlutoAPIError("Pluto channel list failed: HTTP %s" % resp.status_code)

    body = resp.json()
    # Handle the new direct list format
    raw_channels = body if isinstance(body, list) else body.get("data", [])

    channels = []
    for ch in raw_channels:
        ch_id = ch.get("id") or ch.get("_id")
        if not ch_id:
            continue

        name = ch.get("name") or "Unknown Channel"

        # Updated logo parsing for the new API structure
        logo = None
        color_logo = ch.get("colorLogoPNG")
        if isinstance(color_logo, dict):
            logo = color_logo.get("path")
        elif isinstance(color_logo, str):
            logo = color_logo
        
        if not logo: # Fallback
            solid_logo = ch.get("solidLogoPNG")
            if isinstance(solid_logo, dict):
                logo = solid_logo.get("path")

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

    channels.sort(key=lambda c: c["number"])
    return channels
