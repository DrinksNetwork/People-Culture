// Builds dist/site and dist/campaign from public/ and fails if any internal link or local image is broken,
// if any page loads an asset from a host other than drinksnetwork.com.au or Google Fonts, or references Claude-hosted content.
// Images still loading from the old WordPress site are listed as a warning: run "npm run import:wordpress" to copy them in.
import { cpSync, rmSync, mkdirSync, readdirSync, readFileSync, existsSync, statSync } from 'node:fs';
import { join, dirname, resolve, extname } from 'node:path';

const root = resolve(dirname(new URL(import.meta.url).pathname), '..');
const pub = join(root, 'public');
const dist = join(root, 'dist');

rmSync(dist, { recursive: true, force: true });
mkdirSync(join(dist, 'site'), { recursive: true });
mkdirSync(join(dist, 'campaign'), { recursive: true });
for (const f of readdirSync(pub)) if (f !== 'campaign') cpSync(join(pub, f), join(dist, 'site', f), { recursive: true });
cpSync(join(pub, 'campaign'), join(dist, 'campaign', 'pages'), { recursive: true });
cpSync(join(pub, 'media'), join(dist, 'campaign', 'media'), { recursive: true });
cpSync(join(pub, 'assets'), join(dist, 'campaign', 'assets'), { recursive: true });

const ASSET_HOSTS = ['drinksnetwork.com.au', 'fonts.googleapis.com', 'fonts.gstatic.com'];
const errors = [], legacy = new Set();
let pages = 0, links = 0, assets = 0;

// Resolve a root-relative or relative URL the way the site server does: /x -> x.html, x/index.html or x
function resolveLocal(fromFile, url) {
  const clean = url.split(/[?#]/)[0];
  if (!clean) return true;
  const base = clean.startsWith('/') ? join(pub, clean) : resolve(dirname(fromFile), clean);
  return [base, base + '.html', join(base, 'index.html')].some(p => existsSync(p) && (statSync(p).isFile()));
}

function walk(dir) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) { if (f !== 'media' && f !== 'assets') walk(p); continue; }
    if (extname(f) !== '.html') continue;
    pages++;
    const html = readFileSync(p, 'utf8');
    const rel = p.slice(pub.length + 1);
    if (/claude\.ai|\/_blob\//i.test(html)) errors.push(`${rel}: references Claude-hosted content`);
    if (/href="#"/.test(html)) errors.push(`${rel}: has a placeholder link (href="#")`);
    for (const m of html.matchAll(/<(a|link)\b[^>]*\shref="([^"]+)"/g)) {
      const url = m[2];
      if (/^(#|mailto:|tel:)/.test(url) || /^https?:\/\//.test(url)) continue;
      links++;
      if (!resolveLocal(p, url)) errors.push(`${rel}: broken link ${url}`);
    }
    for (const m of html.matchAll(/\s(?:src|poster)="([^"]+)"/g)) {
      const url = m[1];
      assets++;
      if (/^https?:\/\//.test(url)) {
        const host = new URL(url).hostname;
        if (!ASSET_HOSTS.some(h => host === h || host.endsWith('.' + h))) errors.push(`${rel}: loads an asset from ${host}`);
        if (/drinksnetwork\.com\.au\/wp-content\//.test(url)) legacy.add(url);
        continue;
      }
      if (!resolveLocal(p, url)) errors.push(`${rel}: missing file ${url}`);
    }
  }
}
walk(pub);

if (errors.length) {
  console.error(`Build FAILED — ${errors.length} problem(s):\n` + errors.map(e => '  - ' + e).join('\n'));
  process.exit(1);
}
console.log(`Build OK — ${pages} pages, ${links} internal links and ${assets} images/videos checked, output in dist/site and dist/campaign`);
if (legacy.size) console.log(`Note: ${legacy.size} images/videos still load from the old WordPress site. Run "npm run import:wordpress" to copy them into public/media/legacy.`);
