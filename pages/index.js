export default function Home() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Pluto TV Free Channels</h1>
      <p>M3U playlist available at: <code>/api/playlist</code></p>
      <p>JSON channels available at: <code>/api/channels</code></p>
      <h2>How to use:</h2>
      <ol>
        <li>Copy the M3U playlist URL: <code>/api/playlist</code></li>
        <li>Use it in your media player or Kodi addon</li>
        <li>Enjoy Pluto TV free channels!</li>
      </ol>
    </div>
  );
}
