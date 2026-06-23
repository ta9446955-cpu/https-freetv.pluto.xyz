import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  try {
    const filePath = path.join(process.cwd(), 'public', 'channels.json');
    const data = fs.readFileSync(filePath, 'utf8');
    const channels = JSON.parse(data);
    res.status(200).json(channels);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load channels', details: error.message });
  }
}
