def get_stream_url(self, channel_id):
    if not self.session_token:
        self.boot()

    device_id = str(uuid.uuid4())
    sid = str(uuid.uuid4())

    base = "https://stitcher-ipv4.pluto.tv/v1/stitch/embed/hls/channel/{0}/master.m3u8".format(channel_id)

    params = {
        "advertisingId": "",
        "appName": "web",
        "appStoreUrl": "",
        "appVersion": "unknown",
        "app_name": "",
        "architecture": "",
        "buildVersion": "",
        "clientTime": "0",
        "deviceDNT": "0",
        "deviceId": device_id,
        "deviceLat": "",
        "deviceLon": "",
        "deviceMake": "Chrome",
        "deviceModel": "web",
        "deviceType": "web",
        "deviceVersion": "unknown",
        "includeExtendedEvents": "false",
        "marketingRegion": "US",
        "serverSideAds": "true",
        "sid": sid,
        "terminate": "false",
        "userId": "",
        "jwt": self.session_token,
    }

    query = "&".join(
        "%s=%s" % (k, requests.utils.quote(str(v), safe=""))
        for k, v in params.items()
    )
    return "%s?%s" % (base, query)
