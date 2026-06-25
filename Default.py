# -*- coding: utf-8 -*-
"""
default.py
Entry point for the Pluto TV Free Kodi addon.
"""

import sys
import urllib.parse
import os

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# ============================================================
# BULLETPROOF IMPORT FIX
# ============================================================

# Get the folder where THIS file (default.py) lives
addon_dir = os.path.dirname(os.path.abspath(__file__))

# Try resources/lib first
lib_path = os.path.join(addon_dir, 'resources', 'lib')
sys.path.insert(0, lib_path)

# Also add the addon root as fallback (in case pluto_api.py is there)
sys.path.insert(0, addon_dir)

# Debug log so we can verify paths in the Kodi log
xbmc.log("Pluto Free: addon_dir = %s" % addon_dir, xbmc.LOGINFO)
xbmc.log("Pluto Free: lib_path = %s" % lib_path, xbmc.LOGINFO)
xbmc.log("Pluto Free: sys.path[0] = %s" % sys.path[0], xbmc.LOGINFO)
xbmc.log("Pluto Free: sys.path[1] = %s" % sys.path[1], xbmc.LOGINFO)

# Check if pluto_api.py actually exists
api_file_path = os.path.join(lib_path, 'pluto_api.py')
api_file_path2 = os.path.join(addon_dir, 'pluto_api.py')
xbmc.log("Pluto Free: pluto_api.py in lib? %s" % os.path.exists(api_file_path), xbmc.LOGINFO)
xbmc.log("Pluto Free: pluto_api.py in root? %s" % os.path.exists(api_file_path2), xbmc.LOGINFO)

# Now import
try:
    from pluto_api import PlutoClient, PlutoAPIError
    xbmc.log("Pluto Free: pluto_api imported successfully!", xbmc.LOGINFO)
except ImportError as e:
    xbmc.log("Pluto Free: FAILED to import pluto_api: %s" % str(e), xbmc.LOGERROR)
    xbmcgui.Dialog().ok(
        "Pluto TV Free - Import Error",
        "Cannot find pluto_api.py.\n\n"
        "Make sure pluto_api.py is in:\n"
        "%s\n\nor:\n%s" % (lib_path, addon_dir)
    )
    raise  # Re-raise so Kodi shows the error in the log

# ============================================================

ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]


def get_url(**kwargs):
    """Build a plugin URL with URL-encoded values."""
    parts = []
    for key, value in kwargs.items():
        parts.append("%s=%s" % (key, urllib.parse.quote(str(value), safe='')))
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
        xbmcgui.Dialog().ok(
            "Pluto TV Free",
            "Connected to Pluto OK, but the channel list came back empty."
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
    params = dict(urllib.parse.parse_qsl(paramstring))
    if params.get("action") == "play":
        stream_url = urllib.parse.unquote(params["stream"])
        play_channel(stream_url)
    else:
        list_channels()


if __name__ == "__main__":
    query = sys.argv[2][1:] if len(sys.argv) > 2 and sys.argv[2] else ""
    router(query)
