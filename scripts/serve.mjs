// Minimal static preview server for public/ (no dependencies). Usage: npm run preview -> http://localhost:3000
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { join, extname, resolve, dirname } from 'node:path';

const pub = resolve(dirname(new URL(import.meta.url).pathname), '..', 'public');
const types = { '.html': 'text/html; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml' };
const port = Number(process.env.PORT) || 3000;

createServer(async (req, res) => {
  const path = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  const base = join(pub, path);
  if (!base.startsWith(pub)) { res.writeHead(403).end(); return; }
  let file = null;
  for (const c of [base, base + '.html', join(base, 'index.html')]) {
    try { if ((await stat(c)).isFile()) { file = c; break; } } catch {}
  }
  if (!file) { res.writeHead(404, { 'Content-Type': 'text/plain' }).end('Not found'); return; }
  res.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream' });
  res.end(await readFile(file));
}).listen(port, () => console.log(`Preview: http://localhost:${port}  (campaign page: /campaign/bar-takeover)`));
