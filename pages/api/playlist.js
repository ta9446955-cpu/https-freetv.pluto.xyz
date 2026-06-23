import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  try {
    const filePath = path.join(process.cwd(), 'public', 'channels.json');
    const data = fs.readFileSync(filePath, 'utf8');
    const channels = JSON.parse(data);

    let m3u = '#EXTM3U\n';
    channels.forEach(channel => {
      m3u += `#EXTINF:-1 tvg-logo="${channel.logo}" group-title="${channel.category}",${channel.name}\n`;
      m3u += `${channel.stream_url}\n`;
    });

    res.setHeader('Content-Type', 'application/vnd.apple.mpegurl');
    res.status(200).send(m3u);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load playlist', details: error.message });
  }
}
