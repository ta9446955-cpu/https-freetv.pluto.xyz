import fs from 'fs'
import path from 'path'

export default function handler(req, res) {
  try {
    const file = path.join(process.cwd(), 'public', 'channels.json')
    const raw = fs.readFileSync(file, 'utf8')
    const channels = JSON.parse(raw)
    res.setHeader('Content-Type', 'application/json')
    res.status(200).json(channels)
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Unable to read channels.json' })
  }
}
