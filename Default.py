def play_channel(stream_url):
    xbmc.log("Pluto Free: Playing %s" % stream_url, xbmc.LOGINFO)

    headers = (
        "User-Agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
        "&Referer=https://pluto.tv/"
        "&Origin=https://pluto.tv"
    )

    play_item = xbmcgui.ListItem(
        path=stream_url + "|" + headers
    )

    play_item.setMimeType("application/vnd.apple.mpegurl")
    play_item.setContentLookup(False)

    # Kodi 21+
    play_item.setProperty(
        "inputstream",
        "inputstream.adaptive"
    )

    xbmcplugin.setResolvedUrl(
        ADDON_HANDLE,
        True,
        listitem=play_item
  )
