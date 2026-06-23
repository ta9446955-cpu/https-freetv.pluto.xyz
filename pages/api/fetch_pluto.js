export default async function handler(req, res) {
  try {
    const candidates = [
      process.env.PLUTO_CATALOG_URL,
      'https://api.pluto.tv/v3/channels',
      'https://service.pluto.tv/v3/channels'
    ].filter(Boolean)

    let data = null
    let used = null
    for (const url of candidates) {
      try {
        const r = await fetch(url, { headers: { 'User-Agent': 'pluto-fetcher/1.0' } })
        if (!r.ok) continue
        const json = await r.json()
        if (Array.isArray(json)) {
          data = json
          used = url
          break
        }
        if (json && Array.isArray(json.channels)) {
          data = json.channels
          used = url
          break
        }
      } catch (e) {
        // try next
      }
    }

    if (!data) {
      res.status(502).json({ error: 'No catalog found', tried: candidates })
      return
    }

    const channels = data.map((item) => ({
      id: item.id || item.channel_id || item.tvg_id || (item.name && item.name.replace(/\s+/g, '-').toLowerCase()),
      name: item.name || item.title || item.display_name || '',
      logo: item.image || (item.images && (item.images.logo || item.images.thumbnail)) || '',
      category: item.category || item.genre || item.group || '',
      stream_url: item.stream_url || (item.urls && (item.urls.hls || item.urls.hls_url)) || ''
    }))

    res.setHeader('Content-Type', 'application/json')
    res.status(200).json({ source: used || 'unknown', channels })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'fetch failed' })
  }
}
