# -*- coding: utf-8 -*-
"""
default.py
Entry point for the Pluto TV Free Kodi addon.
Lists Pluto TV's live channels and plays the selected one.
"""

import sys
import urllib.parse as urlparse

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
    return "{0}?{1}".format(BASE_URL, urlparse.urlencode(kwargs))


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
        xbmcgui.Dialog().ok(
            "Pluto TV Free",
            "Connected to Pluto OK, but the channel list came back empty. "
            "session_token=%s" % ("yes" if client.session_token else "no")
        )
        xbmcplugin.endOfDirectory(ADDON_HANDLE, succeeded=False)
        return

    for ch in channels:
        list_item = xbmcgui.ListItem(label=ch["name"])
        list_item.setInfo("video", {"title": ch["name"], "mediatype": "video"})
        list_item.setProperty("IsPlayable", "true")
        if ch.get("logo"):
            list_item.setArt({"thumb": ch["logo"], "icon": ch["logo"], "fanart": ch["logo"]})

        url = get_url(action="play", stream=ch["stream_url"])
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, isFolder=False)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def play_channel(stream_url):
    play_item = xbmcgui.ListItem(path=stream_url)
    play_item.setMimeType("application/vnd.apple.mpegurl")
    play_item.setContentLookup(False)
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem=play_item)


def router(paramstring):
    params = dict(urlparse.parse_qsl(paramstring))
    if params.get("action") == "play":
        play_channel(params["stream"])
    else:
        list_channels()


if __name__ == "__main__":
    router(sys.argv[2][1:])
