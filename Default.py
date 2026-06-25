# -*- coding: utf-8 -*-
import sys
import urllib.parse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

sys.path.insert(0, xbmcaddon.Addon(id="plugin.video.pluto_free").getAddonInfo("path") + "/resources/lib")

from pluto_api import PlutoClient, PlutoAPIError  # noqa: E402

ADDON = xbmcaddon.Addon(id="plugin.video.pluto_free")
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]


def get_url(**kwargs):
    parts = []
    for key, value in kwargs.items():
        parts.append("%s=%s" % (key, urllib.parse.quote(str(value), safe="")))
    return "{0}?{1}".format(BASE_URL, "&".join(parts))


def list_channels():
    xbmcplugin.setContent(ADDON_HANDLE, "videos")

    client = PlutoClient()
    try:
        channels = client.get_channels()
    except PlutoAPIError as e:
        xbmc.log("Pluto Free: %s" % e, xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Pluto TV Free - Error", str(e))
        xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=False)
        return
    except Exception as e:
        xbmc.log("Pluto Free: unexpected error: %s" % e, xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Pluto TV Free - Unexpected Error", "%s: %s" % (type(e).__name__, e))
        xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=False)
        return

    if not channels:
        xbmcgui.Dialog().ok("Pluto TV Free", "Connected to Pluto OK, but the channel list came back empty.")
        xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=False)
        return

    for ch in channels:
        list_item = xbmcgui.ListItem(label=ch["name"])
        list_item.setInfo("video", {"title": ch["name"], "mediatype": "video"})
        list_item.setProperty("IsPlayable", "true")
        if ch.get("logo"):
            list_item.setArt({"thumb": ch["logo"], "icon": ch["logo"], "fanart": ch["logo"]})

        url = get_url(action="play", channel_id=ch["id"])
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, isFolder=False)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def play_channel(channel_id):
    client = PlutoClient()
    stream_url = client.get_stream_url(channel_id)

    xbmc.log("Pluto Free stream_url=%s" % stream_url, xbmc.LOGERROR)

    play_item = xbmcgui.ListItem(path=stream_url)
    play_item.setProperty("IsPlayable", "true")
    play_item.setMimeType("application/vnd.apple.mpegurl")
    play_item.setContentLookup(False)

    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem=play_item)


def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    if params.get("action") == "play":
        play_channel(params["channel_id"])
    else:
        list_channels()


if __name__ == "__main__":
    query = sys.argv[2][1:] if len(sys.argv) > 2 and sys.argv[2] else ""
    router(query)
