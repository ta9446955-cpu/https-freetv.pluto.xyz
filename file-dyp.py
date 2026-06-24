import sys
import xbmcgui
import xbmcplugin
import requests

HANDLE = int(sys.argv[1])
M3U_URL = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"

def list_channels():
    li = xbmcgui.ListItem(label="Pluto TV Channel 1")
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(HANDLE, M3U_URL, li, False)
    xbmcplugin.endOfDirectory(HANDLE)

if __name__ == '__main__':
    list_channels()