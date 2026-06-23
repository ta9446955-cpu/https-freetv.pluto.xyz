import fs from 'fs'
import path from 'path'

export default function handler(req, res) {
  try {
    const file = path.join(process.cwd(), 'public', 'channels.json')
    const raw = fs.readFileSync(file, 'utf8')
    const channels = JSON.parse(raw)

    let m3u = '#EXTM3U\n'
    for (const c of channels) {
      const tvgLogo = c.logo ? `tvg-logo="${c.logo}"` : ''
      const group = c.category ? `group-title="${c.category}"` : ''
      m3u += `#EXTINF:-1 tvg-id="${c.id}" tvg-name="${c.name}" ${tvgLogo} ${group},${c.name}\n${c.stream_url}\n`
    }

    res.setHeader('Content-Type', 'application/vnd.apple.mpegurl')
    res.setHeader('Content-Disposition', 'attachment; filename="pluto-channels.m3u"')
    res.status(200).send(m3u)
  } catch (err) {
    console.error(err)
    res.status(500).send('Error building playlist')
  }
}
