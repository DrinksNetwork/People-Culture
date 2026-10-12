// One-off import from the old WordPress site (www.drinksnetwork.com.au). Run on a machine with internet access:
//   npm run import:wordpress
// It (1) copies every blog post word for word into public/blog/<slug>.html and rebuilds public/blog/index.html,
// (2) copies the privacy policy, cookie policy and user terms into their pages, and
// (3) downloads every wp-content/uploads image or video referenced anywhere in public/ into public/media/legacy/
//     and rewrites those references, so nothing depends on the old WordPress site afterwards.
// Safe to run more than once. Uses the public WordPress REST API — no login needed.
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';

const ROOT = resolve(dirname(new URL(import.meta.url).pathname), '..');
const PUB = join(ROOT, 'public');
const OLD = process.env.WP_BASE || 'https://www.drinksnetwork.com.au';
const API = `${OLD}/wp-json/wp/v2`;
const HEADER = readFileSync(join(ROOT, 'scripts/partials/header.html'), 'utf8');
const FOOTER = readFileSync(join(ROOT, 'scripts/partials/footer.html'), 'utf8');
const LEGAL = [
  { wp: 'privacy-policy', out: 'privacy-policy', title: 'Privacy policy' },
  { wp: 'cookie-policy', out: 'cookie-policy', title: 'Cookie policy' },
  { wp: 'user-terms-2', out: 'user-terms', title: 'User terms' },
];

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const text = s => String(s).replace(/<[^>]+>/g, '').replace(/&#8217;/g, '’').replace(/&#8211;/g, '–').replace(/&amp;/g, '&').replace(/&#038;/g, '&').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();

async function getJSON(url) {
  const r = await fetch(url, { headers: { 'User-Agent': 'DrinksNetwork-site-import' } });
  if (!r.ok) throw new Error(`${r.status} ${url}`);
  return { data: await r.json(), total: Number(r.headers.get('x-wp-totalpages') || 1) };
}

// Strip page-builder clutter but keep the words, headings, lists, links, images and embeds.
// Old WordPress page addresses -> new site paths
const PAGE_MAP = {
  'privacy-policy': '/privacy-policy', 'cookie-policy': '/cookie-policy', 'user-terms-2': '/user-terms',
  'repshare': '/brands', 'repshare-producer': '/reps', 'securicode': '/securicode', 'about-us': '/about',
  'contact-drinks-network': '/contact', 'contact': '/contact', 'frequently-asked-questions': '/faqs',
  'learn-spirits-wine-hospitality-skills': '/courses', 'blog': '/blog', 'liquor-industry-people-and-culture': '/blog',
};
const HOSTS = ['https://www.drinksnetwork.com.au', 'https://drinksnetwork.com.au', 'http://www.drinksnetwork.com.au', 'http://drinksnetwork.com.au'];

function relink(html, postSlugs = []) {
  let out = String(html);
  for (const host of HOSTS) {
    for (const slug of postSlugs) out = out.split(`${host}/${slug}/`).join(`/blog/${slug}`).split(`${host}/${slug}"`).join(`/blog/${slug}"`);
    for (const [from, to] of Object.entries(PAGE_MAP)) out = out.split(`${host}/${from}/`).join(to).split(`${host}/${from}"`).join(`${to}"`);
  }
  return out;
}

function clean(html, postSlugs = []) {
  return relink(html, postSlugs)
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<noscript[\s\S]*?<\/noscript>/gi, '')
    .replace(/\s(on\w+)="[^"]*"/gi, '')
    .replace(/\s(class|id|style|data-[\w-]+|sizes|srcset|decoding|fetchpriority)="[^"]*"/gi, '')
    .replace(/<(div|span|section)>\s*<\/\1>/gi, '')
    .replace(/\shref="#"/gi, '')                       // empty WordPress anchors are not links
    .replace(/href="([^"]*?)\\+"/g, 'href="$1"')         // stray backslashes from escaped JSON
    .replace(/<img /gi, '<img loading="lazy" ');
}

function shell({ path, title, desc, body, current, ld = [] }) {
  const hdr = current ? HEADER.replace(`<a href="${current}">`, `<a href="${current}" aria-current="page">`) : HEADER;
  const lds = ld.map(x => `<script type="application/ld+json">${JSON.stringify(x)}</script>`).join('\n');
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="https://site.drinksnetwork.com.au/${path}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Drinks Network">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Archivo+Narrow:wght@500;700&amp;family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400;1,8..60,600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
${lds}
</head>
<body>
${hdr}
<main>
${body}
</main>
${FOOTER}
<script src="/assets/site.js" defer></script>
</body>
</html>
`;
}

const fmtDate = d => new Date(d).toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' });

async function importPosts() {
  const posts = [];
  for (let page = 1, total = 1; page <= total; page++) {
    const { data, total: t } = await getJSON(`${API}/posts?per_page=100&page=${page}&_embed=1`);
    total = t; posts.push(...data);
  }
  mkdirSync(join(PUB, 'blog'), { recursive: true });
  const slugs = posts.map(p => p.slug);
  const cards = [];
  for (const p of posts) {
    const title = text(p.title.rendered);
    const author = p._embedded?.author?.[0]?.name || 'Drinks Network';
    const hero = p._embedded?.['wp:featuredmedia']?.[0]?.source_url || '';
    const cat = p._embedded?.['wp:term']?.[0]?.[0]?.name || 'People & Culture';
    const excerpt = text(p.excerpt.rendered).replace(/\s*\[…\]$|\s*…$/, '…');
    const body = `<article class="wrap" style="max-width:860px;padding-top:56px;padding-bottom:72px">
<a class="kick" href="/blog" style="font-size:11px;text-decoration:none">← People &amp; Culture</a>
<div class="kick" style="color:var(--red);margin-top:20px">${esc(cat)}</div>
<h1 class="display" style="font-size:clamp(44px,6vw,84px);margin:12px 0 14px">${esc(title)}</h1>
<p class="kick" style="font-size:12px;color:var(--quiet);margin:0 0 24px">By ${esc(author)} · <time datetime="${p.date.slice(0, 10)}">${fmtDate(p.date)}</time></p>
${hero ? `<img src="${hero}" alt="" style="width:100%;height:auto;display:block;background:var(--sand)">` : ''}
<div class="prose" style="margin-top:28px">
${clean(p.content.rendered, slugs)}
</div>
</article>`;
    writeFileSync(join(PUB, 'blog', `${p.slug}.html`), shell({
      path: `blog/${p.slug}`, title: `${title} | Drinks Network`, desc: excerpt.slice(0, 155), body, current: '/blog',
      ld: [{ '@context': 'https://schema.org', '@type': 'BlogPosting', headline: title, datePublished: p.date, author: { '@type': 'Person', name: author }, image: hero || undefined }],
    }));
    cards.push(`<a href="/blog/${p.slug}" style="text-decoration:none;color:var(--ink);display:flex;flex-direction:column;gap:10px">
${hero ? `<img src="${hero}" alt="" loading="lazy" style="width:100%;aspect-ratio:16/10;object-fit:cover;display:block;background:var(--sand)">` : ''}
<span class="kick" style="font-size:11px;color:var(--red)">${esc(cat)}</span>
<span class="display" style="font-size:32px;line-height:1">${esc(title)}</span>
<span style="font-size:17px;line-height:1.45;color:var(--body)">${esc(excerpt)}</span>
<span class="kick" style="font-size:11px;color:var(--quiet)">By ${esc(author)} · ${fmtDate(p.date)}</span></a>`);
  }
  const index = `<section style="background:var(--paper)"><div class="wrap" style="padding-top:56px;padding-bottom:48px">
<div class="kick" style="color:var(--red)">Our people. Our pages.</div>
<h1 class="display" style="font-size:clamp(56px,8vw,120px);margin:14px 0 18px">People &amp; Culture</h1>
<p style="font-size:23px;font-style:italic;line-height:1.4;max-width:820px;margin:0">Our blogs cover drinks industry stories, politics and liquor. Stay up to date on news, reviews and brands.</p>
</div></section>
<section class="wrap" style="padding-bottom:72px"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:36px 28px;border-top:3px solid var(--ink);padding-top:28px">
${cards.join('\n')}
</div></section>`;
  writeFileSync(join(PUB, 'blog', 'index.html'), shell({ path: 'blog', title: 'People & Culture: Drinks Industry Stories | Drinks Network',
    desc: 'Drinks industry stories, politics and liquor: news, reviews and brands from the Drinks Network team.', body: index, current: '/blog' }));
  console.log(`Blog: ${posts.length} posts imported`);
  return posts.map(p => p.slug);
}

async function importLegal() {
  for (const l of LEGAL) {
    const { data } = await getJSON(`${API}/pages?slug=${l.wp}`);
    if (!data.length) { console.warn(`Legal: ${l.wp} not found, kept placeholder`); continue; }
    const body = `<article class="wrap" style="max-width:860px;padding-top:56px;padding-bottom:72px">
<div class="kick" style="color:var(--red)">Legal</div>
<h1 class="display" style="font-size:clamp(48px,6vw,96px);margin:12px 0 24px">${esc(l.title)}</h1>
<div class="prose">
${clean(data[0].content.rendered)}
</div>
</article>`;
    writeFileSync(join(PUB, `${l.out}.html`), shell({ path: l.out, title: `${l.title} | Drinks Network`, desc: `The Drinks Network ${l.title.toLowerCase()}.`, body }));
    console.log(`Legal: ${l.out} imported`);
  }
}

function htmlFiles(dir) {
  return readdirSync(dir).flatMap(f => {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) return f === 'media' ? [] : htmlFiles(p);
    return f.endsWith('.html') || f.endsWith('.json') ? [p] : []; // course data files carry images too
  });
}

async function localiseMedia() {
  const re = /https?:\/\/(?:www\.)?drinksnetwork\.com\.au\/wp-content\/uploads\/([^"'\s)<>]+?\.(?:png|jpe?g|gif|webp|svg|mp4|webm))/gi;
  let downloaded = 0, failed = 0;
  for (const file of htmlFiles(PUB)) {
    let html = readFileSync(file, 'utf8');
    const urls = [...new Set([...html.matchAll(re)].map(m => m[0]))];
    for (const url of urls) {
      const rel = decodeURIComponent(url.replace(re, '$1'));
      const dest = join(PUB, 'media', 'legacy', rel);
      if (!existsSync(dest)) {
        try {
          const r = await fetch(url);
          if (!r.ok) throw new Error(r.status);
          mkdirSync(dirname(dest), { recursive: true });
          writeFileSync(dest, Buffer.from(await r.arrayBuffer()));
          downloaded++;
        } catch (e) { failed++; console.warn(`Media: could not download ${url} (${e.message}) — left pointing at the old site`); continue; }
      }
      html = html.split(url).join(`/media/legacy/${rel}`);
    }
    writeFileSync(file, html);
  }
  console.log(`Media: ${downloaded} files downloaded into public/media/legacy, ${failed} failed`);
}

try { await importPosts(); } catch (e) { console.error('Blog import failed:', e.message); }
try { await importLegal(); } catch (e) { console.error('Legal import failed:', e.message); }
await localiseMedia();
console.log('Done. Run "npm run build" to check every link and image.');
