// Builds dist/site and dist/campaign from public/, and fails if any local link or image is broken
// or if any page references an external host other than drinksnetwork.com.au and Google Fonts.
import { cpSync, rmSync, mkdirSync, readdirSync, readFileSync, existsSync, statSync } from 'node:fs';
import { join, dirname, resolve, extname } from 'node:path';

const root = resolve(dirname(new URL(import.meta.url).pathname), '..');
const pub = join(root, 'public');
const dist = join(root, 'dist');

rmSync(dist, { recursive: true, force: true });
mkdirSync(join(dist, 'site'), { recursive: true });
mkdirSync(join(dist, 'campaign'), { recursive: true });

// site.drinksnetwork.com.au: top-level pages + media
for (const f of readdirSync(pub)) {
  if (f === 'campaign') continue;
  cpSync(join(pub, f), join(dist, 'site', f), { recursive: true });
}
// campaign.drinksnetwork.com.au: campaign pages at the root, media one level up as in public/
cpSync(join(pub, 'campaign'), join(dist, 'campaign', 'pages'), { recursive: true });
cpSync(join(pub, 'media'), join(dist, 'campaign', 'media'), { recursive: true });

const ALLOWED_HOSTS = ['drinksnetwork.com.au', 'fonts.googleapis.com', 'fonts.gstatic.com'];
const errors = [];
let pages = 0, refs = 0;

function walk(dir) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) { if (f !== 'media') walk(p); continue; }
    if (extname(f) !== '.html') continue;
    pages++;
    const html = readFileSync(p, 'utf8');
    if (/claude\.ai|\/_blob\//i.test(html)) errors.push(`${p}: references Claude-hosted content`);
    for (const m of html.matchAll(/(?:src|href)="([^"]+)"/g)) {
      const url = m[1];
      if (url.startsWith('#') || url.startsWith('mailto:') || url.startsWith('tel:')) continue;
      if (/^https?:\/\//.test(url)) {
        const host = new URL(url).hostname;
        if (!ALLOWED_HOSTS.some(h => host === h || host.endsWith('.' + h))) errors.push(`${p}: external host ${host}`);
        continue;
      }
      refs++;
      const target = resolve(dirname(p), url.split(/[?#]/)[0]);
      if (!existsSync(target)) errors.push(`${p}: missing ${url}`);
    }
  }
}
walk(pub);

if (errors.length) {
  console.error(`Build FAILED — ${errors.length} problem(s):\n` + errors.map(e => '  - ' + e).join('\n'));
  process.exit(1);
}
console.log(`Build OK — ${pages} pages, ${refs} local links/images checked, output in dist/site and dist/campaign`);
