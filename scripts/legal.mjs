// Builds the legal pages from content/legal/*.md (the RepShare terms written in Claude Docs).
//   npm run legal      -> public/legal/<slug>.html + public/legal/index.html
// To update a document: replace its markdown file in content/legal/ with the latest export and run this again.
// The Subcontractor Agreement is deliberately NOT published: it is issued to Representatives inside RepShare.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';

const ROOT = resolve(dirname(new URL(import.meta.url).pathname), '..');
const SRC = join(ROOT, 'content', 'legal');
const OUT = join(ROOT, 'public', 'legal');
const HEADER = readFileSync(join(ROOT, 'scripts', 'partials', 'header.html'), 'utf8');
const FOOTER = readFileSync(join(ROOT, 'scripts', 'partials', 'footer.html'), 'utf8');

export const DOCS = [
  { slug: 'terms-of-use', file: 'terms-of-use.md', title: 'RepShare Terms of Use', short: 'Terms of Use', who: 'Everyone who uses RepShare or this website', desc: 'The RepShare Terms of Use: accounts, proper use, signing in the app, confidentiality and disputes.' },
  { slug: 'service-terms', file: 'service-terms.md', title: 'RepShare Service Terms', short: 'Service Terms', who: 'Brands (Vendors), Representatives and Buyers', desc: 'How Drinks Network agency services work: Briefs and Jobs, Vendor and Representative obligations, orders, content and ending services.' },
  { slug: 'payment-terms', file: 'payment-terms.md', title: 'RepShare Payment Terms', short: 'Payment Terms', who: 'Brands (Vendors), Representatives and Buyers', desc: 'How money moves in RepShare: prepaid subscriptions and top-ups for Vendors, cash-outs for Representatives, and how Buyers pay.' },
  { slug: 'privacy-policy', file: 'privacy-policy.md', title: 'RepShare Privacy Policy', short: 'Privacy Policy', who: 'Everyone', desc: 'What personal information Drinks Network collects through RepShare, this website and our agency services, and how to access or correct it.' },
];

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const slugify = (s) => s.toLowerCase().replace(/<[^>]+>/g, '').replace(/&[a-z]+;/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
function inline(s) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2">$1</a>')
    .replace(/\b(Service Terms|Payment Terms|Privacy Policy|Terms of Use)\b(?![^<]*<\/a>)/g, (m) => {
      const d = DOCS.find((x) => x.short === m); return d ? `<a href="/legal/${d.slug}">${m}</a>` : m;
    })
    .replace(/([\w.+-]+@drinksnetwork\.com\.au)/g, '<a href="mailto:$1">$1</a>');
}

export function render(md, selfShort) {
  const lines = md.replace(/\r/g, '').split('\n');
  const toc = []; let html = ''; let i = 0; let title = '';
  while (i < lines.length) {
    const l = lines[i];
    if (!l.trim()) { i++; continue; }
    let m;
    if ((m = l.match(/^# (.+)/))) { title = m[1]; i++; continue; }
    if ((m = l.match(/^(#{2,3}) (.+)/))) {
      const lvl = m[1].length, text = m[2], id = slugify(text);
      if (lvl === 2) toc.push({ id, text });
      html += `<h${lvl} id="${id}">${inline(text)}</h${lvl}>\n`; i++; continue;
    }
    if (l.startsWith('|')) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith('|')) { if (!/^\|\s*-/.test(lines[i])) rows.push(lines[i].split('|').slice(1, -1).map((c) => c.trim())); i++; }
      html += '<div class="legal-table"><table><thead><tr>' + rows[0].map((c) => `<th>${inline(c)}</th>`).join('') + '</tr></thead><tbody>' +
        rows.slice(1).map((r) => '<tr>' + r.map((c) => `<td>${inline(c)}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>\n';
      continue;
    }
    if (/^\([a-z]\) /.test(l)) {
      let items = '';
      for (;;) {
        items += `<li><span class="legal-n">${lines[i].slice(0, 3)}</span> ${inline(lines[i].slice(4))}</li>`;
        let j = i + 1; while (j < lines.length && !lines[j].trim()) j++;
        if (j < lines.length && /^\([a-z]\) /.test(lines[j])) { i = j; continue; }
        i = j; break;
      }
      html += `<ul class="legal-list">${items}</ul>\n`; continue;
    }
    const n = l.match(/^(\d+\.\d+) (.*)/);
    html += n ? `<p id="c-${n[1].replace('.', '-')}"><span class="legal-n">${n[1]}</span> ${inline(n[2])}</p>\n` : `<p>${inline(l)}</p>\n`;
    i++;
  }
  return { title, toc, html };
}

function page({ slug, title, desc, body, canonical }) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} | Drinks Network</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="https://site.drinksnetwork.com.au${canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Drinks Network">
<meta property="og:title" content="${esc(title)} | Drinks Network">
<meta property="og:description" content="${esc(desc)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Archivo+Narrow:wght@500;700&amp;family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400;1,8..60,600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
${HEADER}
<main>
${body}
</main>
${FOOTER}
<script src="/assets/site.js" defer></script>
</body>
</html>
`;
}

const nav = (active) => '<nav class="legal-nav kick" aria-label="Legal documents">' +
  DOCS.map((d) => `<a href="/legal/${d.slug}"${d.slug === active ? ' aria-current="page"' : ''}>${d.short}</a>`).join('') +
  '<a href="/cookie-policy">Cookie Policy</a></nav>';

mkdirSync(OUT, { recursive: true });
for (const d of DOCS) {
  const { title, toc, html } = render(readFileSync(join(SRC, d.file), 'utf8'), d.short);
  const body = `<section class="wrap legal-doc">
<div class="kick" style="color:var(--red)">Legal · ${esc(d.who)}</div>
<h1 class="display" style="font-size:clamp(44px,6vw,92px);margin:12px 0 18px">${esc(title || d.title)}</h1>
${nav(d.slug)}
<div class="legal-grid">
<aside class="legal-toc"><div class="kick" style="color:var(--red)">Contents</div><ol>${toc.map((t) => `<li><a href="#${t.id}">${inline(t.text)}</a></li>`).join('')}</ol></aside>
<article class="legal-body prose">
${html}
</article>
</div>
</section>`;
  writeFileSync(join(OUT, `${d.slug}.html`), page({ slug: d.slug, title: d.title, desc: d.desc, body, canonical: `/legal/${d.slug}` }));
}

const cards = DOCS.map((d) => `<a class="legal-card" href="/legal/${d.slug}"><span class="kick" style="color:var(--red)">${esc(d.who)}</span><span class="display" style="font-size:34px">${esc(d.short)}</span><span>${esc(d.desc)}</span></a>`).join('');
const index = `<section class="wrap legal-doc">
<div class="kick" style="color:var(--red)">Legal</div>
<h1 class="display" style="font-size:clamp(48px,7vw,104px);margin:12px 0 18px">Terms &amp; policies</h1>
<p style="font-size:21px;font-style:italic;max-width:780px;margin:0 0 28px">The terms behind RepShare and Drinks Network. The Terms of Use and Privacy Policy apply to everyone. The Service and Payment Terms have a part for each kind of user.</p>
<div class="legal-cards">${cards}<a class="legal-card" href="/cookie-policy"><span class="kick" style="color:var(--red)">Website visitors</span><span class="display" style="font-size:34px">Cookie Policy</span><span>How this website uses cookies.</span></a></div>
<h2 class="display" style="font-size:clamp(32px,4vw,56px);margin:48px 0 16px">Which terms apply to you</h2>
<div class="legal-table"><table><thead><tr><th>You are</th><th>Terms that apply</th></tr></thead><tbody>
<tr><td><strong>A brand or supplier (Vendor)</strong></td><td><a href="/legal/terms-of-use">Terms of Use</a> · <a href="/legal/service-terms#4-vendors">Service Terms §4 Vendors</a> · <a href="/legal/payment-terms#part-a-vendors">Payment Terms Part A</a> · <a href="/legal/privacy-policy">Privacy Policy</a></td></tr>
<tr><td><strong>A rep or brand manager (Representative)</strong></td><td><a href="/legal/terms-of-use">Terms of Use</a> · <a href="/legal/service-terms#5-representatives">Service Terms §5 Representatives</a> · <a href="/legal/payment-terms#part-b-representatives">Payment Terms Part B</a> · <a href="/legal/privacy-policy">Privacy Policy</a>. Your Subcontractor Agreement is issued to you in RepShare when you're onboarded.</td></tr>
<tr><td><strong>A venue or buyer</strong></td><td><a href="/legal/terms-of-use">Terms of Use</a> · <a href="/legal/service-terms#6-orders">Service Terms §6 Orders</a> · <a href="/legal/payment-terms#part-c-buyers">Payment Terms Part C</a> · <a href="/legal/privacy-policy">Privacy Policy</a></td></tr>
<tr><td><strong>Anyone filling in a form on this site</strong></td><td><a href="/legal/privacy-policy">Privacy Policy</a> · <a href="/cookie-policy">Cookie Policy</a></td></tr>
</tbody></table></div>
</section>`;
writeFileSync(join(OUT, 'index.html'), page({ slug: 'index', title: 'Terms & policies', desc: 'RepShare and Drinks Network terms and policies: Terms of Use, Service Terms, Payment Terms and Privacy Policy.', body: index, canonical: '/legal' }));
console.log('Legal pages written:', DOCS.map((d) => d.slug).join(', '), '+ index');
