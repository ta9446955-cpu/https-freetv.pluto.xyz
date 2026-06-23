import { useEffect, useState } from 'react'

export default function Home() {
  const [channels, setChannels] = useState([])
  const [q, setQ] = useState('')

  useEffect(() => {
    fetch('/api/channels')
      .then(r => r.json())
      .then(setChannels)
      .catch(console.error)
  }, [])

  const filtered = channels.filter(c =>
    (c.name || '').toLowerCase().includes(q.toLowerCase()) ||
    (c.category || '').toLowerCase().includes(q.toLowerCase())
  )

  return (
    <main className="container">
      <header>
        <h1>Pluto TV — Free channels</h1>
        <p>Browse your curated list of Pluto channels and open streams or download an M3U playlist.</p>
        <div className="controls">
          <input placeholder="Search channels or category" value={q} onChange={e => setQ(e.target.value)} />
          <a className="playlist-link" href="/api/playlist">Download M3U playlist</a>
        </div>
      </header>

      <section className="grid">
        {filtered.map(ch => (
          <article key={ch.id} className="card">
            <img className="logo" src={ch.logo || '/logo.svg'} alt={`${ch.name} logo`} />
            <h3>{ch.name}</h3>
            <p className="meta">{ch.category}</p>
            <div className="actions">
              <a target="_blank" rel="noopener noreferrer" href={ch.stream_url}>Open stream</a>
            </div>
          </article>
        ))}
        {filtered.length === 0 && <p>No channels found.</p>}
      </section>

      <footer>
        <p>Edit <code>public/channels.json</code> in the repository to add or fix channels.</p>
      </footer>
    </main>
  )
}
