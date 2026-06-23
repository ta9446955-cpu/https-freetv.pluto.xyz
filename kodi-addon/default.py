import sys
import urllib.request
import urllib.error

try:
    import xbmcgui
    import xbmcplugin
    import xbmcaddon
except Exception:
    # Running outside Kodi (for debugging)
    xbmcgui = xbmcplugin = xbmcaddon = None

addon = xbmcaddon.Addon() if xbmcaddon else None
base_url = addon.getSetting('base_url') if addon else None
if not base_url:
    base_url = 'https://your-deploy.vercel.app'

m3u_url = base_url.rstrip('/') + '/api/playlist'


def list_playlists():
    try:
        req = urllib.request.Request(m3u_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode('utf-8')
    except Exception as e:
        if xbmcgui:
            xbmcgui.Dialog().ok('Error', f'Failed to fetch playlist: {e}')
        else:
            print('Failed to fetch playlist:', e)
        return

    lines = data.splitlines()
    handle = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    for i, line in enumerate(lines):
        if line.startswith('#EXTINF'):
            name = line.split(',', 1)[1] if ',' in line else 'Pluto Channel'
            url = lines[i + 1] if i + 1 < len(lines) else None
            if url:
                li = xbmcgui.ListItem(label=name) if xbmcgui else None
                if xbmcplugin:
                    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)
                else:
                    print('Item:', name, url)

    if xbmcplugin:
        xbmcplugin.endOfDirectory(handle)


if __name__ == '__main__':
    list_playlists()
