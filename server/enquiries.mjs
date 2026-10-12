// Drinks Network enquiry handler: drop-in for the RepShare app's POST /api/enquiries.
//
// For every website form it:
//   1. saves the contact in RepShare (the saveContact hook you pass in),
//   2. adds or updates the person in the Mailchimp audience with their tags
//      (Vendor, Rep, Partner, Buyer, Trade, campaign:<slug>, form:<name>, enquiry),
//   3. emails the admin team (Hayden, Manuel, Joe, Emma) with every answer,
//   4. sends the enquirer a confirmation email from Mailchimp about their enquiry.
//
// Step 4 works one of two ways (set either, or both):
//   - Mailchimp Customer Journey: build a journey in Mailchimp that starts when the tag
//     "enquiry" is added and sends the "Thanks for your enquiry" email. The tag added in
//     step 2 starts it, so marketing can edit the email in Mailchimp without code.
//   - Mailchimp Transactional (Mandrill): set MAILCHIMP_TRANSACTIONAL_KEY and the reply below
//     is sent straight away (also used for the admin email in step 3).
//
// Environment (Replit Secrets, never committed):
//   MAILCHIMP_API_KEY            Marketing API key, e.g. abc123-us21 (data centre taken from the suffix)
//   MAILCHIMP_AUDIENCE_ID        Audience (list) id
//   MAILCHIMP_TRANSACTIONAL_KEY  Optional: Mailchimp Transactional (Mandrill) key for instant emails
//   ENQUIRY_FROM_EMAIL           e.g. hello@drinksnetwork.com.au (a verified sending domain)
//   ENQUIRY_ADMIN_EMAILS         Comma list; defaults to the four admins below
//   SITE_URL                     Public site, used for links in emails (default https://site.drinksnetwork.com.au)
//
// Gated briefs (form "tasting-brief"): the reply carries the brief links when sendCopy is true, and each
// address in shareWith (max 3, never the enquirer's own) gets one short email with the same links.
// Links are built here from SITE_URL, never taken from the browser.

import crypto from 'node:crypto';

const DEFAULT_ADMINS = ['hayden@drinksnetwork.com.au', 'manuel@drinksnetwork.com.au', 'joe@drinksnetwork.com.au', 'emma@drinksnetwork.com.au'];
const ALLOWED_TAGS = new Set(['Vendor', 'Rep', 'Partner', 'Buyer', 'Trade']);

const FORM_LABELS = {
  'newsletter': 'Newsletter sign-up',
  'start-here': 'Start here',
  'brands-subscription': 'RepShare subscription request',
  'retail-program': 'Retail Activation enquiry',
  'whisky-adventure-venue': 'Australian Whisky Adventure: venue',
  'whisky-adventure-brand': 'Australian Whisky Adventure: brand',
  'contact': 'Contact form',
  'securicode': 'SecuriCode enquiry',
  'bar-takeover': 'Bar Takeover registration',
  'san-junipero-giveaway': 'San Junipero 5+1 draw entry',
  'tasting-brief': 'Tasting Series partnership brief request',
  'tasting-agreement': 'Tasting Series partner agreement',
};

const SKIP_FIELDS = new Set(['website', 'consent', 'pageUrl', 'utmSource', 'utmMedium', 'utmCampaign', 'sessionId', 'tags', 'form', 'campaign', 'sendCopy']);
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const BRIEFS = {
  'tasting-brief': { title: 'Tasting Series partnership brief', page: '/whisky-adventure/tasting-series?brief=open', pdf: '/media/brief/tasting-partnership-brief.pdf' },
};

export function shareList(p) {
  const own = String(p.email || '').trim().toLowerCase();
  const raw = Array.isArray(p.shareWith) ? p.shareWith : String(p.shareWith || '').split(/[\s,;]+/);
  return [...new Set(raw.map((e) => String(e).trim().toLowerCase()).filter((e) => EMAIL_RE.test(e) && e !== own))].slice(0, 3);
}

export function briefLinks(p, env = {}) {
  const b = BRIEFS[p.form]; if (!b) return null;
  const site = (env.SITE_URL || 'https://site.drinksnetwork.com.au').replace(/\/$/, '');
  return { title: b.title, page: site + b.page, pdf: site + b.pdf };
}

export function shareEmail(p, links) {
  const who = [p.firstName, p.lastName].filter(Boolean).join(' ') || p.email;
  return {
    subject: `${who} shared the Drinks Network ${links.title} with you`,
    html: `<div style="font-family:Arial,sans-serif;font-size:15px;color:#111;max-width:560px"><div style="background:#E42E2E;color:#fff;padding:18px;font-size:22px;font-weight:bold">${esc(links.title)}</div>
<p>${esc(who)}${p.company ? ' from ' + esc(p.company) : ''} thought you should see how a Drinks Network ticketed tasting works: the venue and brand roles, the 50/50 ticket split, fees and what one night can make.</p>
<p><a href="${esc(links.page)}" style="display:inline-block;background:#E42E2E;color:#fff;padding:12px 18px;text-decoration:none;font-weight:bold">Read the brief</a> &nbsp; <a href="${esc(links.pdf)}">Download the A4 PDF</a></p>
<p style="color:#5A554D;font-size:13px">You're getting this one email because ${esc(who)} entered your address. We won't add you to any list.</p>
<p>Drinks Network<br>Sydney · Melbourne · Brisbane</p></div>`,
  };
}

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const label = (k) => k.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/^./, (c) => c.toUpperCase());
const show = (v) => Array.isArray(v) ? v.join(', ') : (v && typeof v === 'object') ? Object.entries(v).map(([k, x]) => `${label(k)}: ${show(x)}`).join('; ') : String(v ?? '');

export function validate(p) {
  if (!p || typeof p !== 'object') return 'Invalid request';
  if (p.website) return 'spam';                                         // honeypot filled in
  if (!p.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(p.email).trim())) return 'A valid email is required';
  if (!p.form || typeof p.form !== 'string') return 'Missing form name';
  return null;
}

export function tagsFor(p) {
  const tags = (Array.isArray(p.tags) ? p.tags : []).filter((t) => ALLOWED_TAGS.has(t));
  if (p.role && ALLOWED_TAGS.has(p.role)) tags.push(p.role);
  if (p.campaign) tags.push(`campaign:${p.campaign}`);
  tags.push(`form:${p.form}`);
  if (p.form !== 'newsletter') tags.push('enquiry');                   // starts the "Thanks for your enquiry" journey
  return [...new Set(tags)];
}

export function answersTable(p) {
  return Object.entries(p).filter(([k, v]) => !SKIP_FIELDS.has(k) && v !== '' && v != null && !(Array.isArray(v) && !v.length))
    .map(([k, v]) => [label(k), show(v)]);
}

async function mailchimp(env, fetchImpl, method, path, body) {
  const key = env.MAILCHIMP_API_KEY; const dc = key.split('-').pop();
  const r = await fetchImpl(`https://${dc}.api.mailchimp.com/3.0${path}`, {
    method, headers: { Authorization: 'Basic ' + Buffer.from('dn:' + key).toString('base64'), 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`Mailchimp ${method} ${path}: ${r.status} ${await r.text()}`);
  return r.status === 204 ? null : r.json();
}

async function transactional(env, fetchImpl, message) {
  const r = await fetchImpl('https://mandrillapp.com/api/1.0/messages/send', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: env.MAILCHIMP_TRANSACTIONAL_KEY, message }),
  });
  if (!r.ok) throw new Error(`Mailchimp Transactional: ${r.status} ${await r.text()}`);
  return r.json();
}

export function adminEmail(p, formLabel) {
  const rows = answersTable(p).map(([k, v]) => `<tr><td style="padding:6px 12px 6px 0;color:#5A554D;vertical-align:top">${esc(k)}</td><td style="padding:6px 0"><strong>${esc(v)}</strong></td></tr>`).join('');
  const who = [p.firstName, p.lastName].filter(Boolean).join(' ') || p.email;
  return {
    subject: `New lead: ${formLabel} · ${p.company || who}${p.package ? ' · ' + p.package : ''}`,
    html: `<div style="font-family:Arial,sans-serif;font-size:15px;color:#111"><div style="background:#E42E2E;color:#fff;padding:14px 18px;font-weight:bold">New ${esc(formLabel)}</div>
<table style="margin:16px 0;border-collapse:collapse">${rows}</table>
<p style="color:#5A554D">Tags: ${esc(tagsFor(p).join(', '))}<br>Page: ${esc(p.pageUrl || '')}<br>Source: ${esc([p.utmSource, p.utmMedium, p.utmCampaign].filter(Boolean).join(' / ') || 'direct')}<br>Marketing consent: ${p.consent ? 'yes' : 'no'}</p></div>`,
  };
}

export function replyEmail(p, formLabel) {
  const name = p.firstName ? p.firstName.split(' ')[0] : 'there';
  const rows = answersTable(p).map(([k, v]) => `<li><strong>${esc(k)}:</strong> ${esc(v)}</li>`).join('');
  return {
    subject: p.form === 'newsletter' ? 'Welcome to Drinks Network' : `We've got your ${formLabel.toLowerCase()}`,
    html: `<div style="font-family:Arial,sans-serif;font-size:15px;color:#111;max-width:560px"><div style="background:#E42E2E;color:#fff;padding:18px;font-size:22px;font-weight:bold">Thanks, ${esc(name)}.</div>
<p>Your ${esc(formLabel.toLowerCase())} has reached the Drinks Network team. Someone will be in touch within one business day.</p>
${p.links ? `<p><a href="${esc(p.links.page)}" style="display:inline-block;background:#E42E2E;color:#fff;padding:12px 18px;text-decoration:none;font-weight:bold">Read the ${esc(p.links.title)}</a> &nbsp; <a href="${esc(p.links.pdf)}">Download the A4 PDF</a></p>` : ''}
${p.form === 'newsletter' ? '' : `<p>Here's what you sent us:</p><ul>${rows}</ul>`}
<p>Good times,<br>Drinks Network<br>Sydney · Melbourne · Brisbane</p></div>`,
  };
}

// Main entry: returns { ok, contact } or throws. Mailchimp and email failures are logged, not fatal,
// so a lead is never lost because a third-party service is down.
export async function handleEnquiry(payload, { env = process.env, fetchImpl = fetch, saveContact = async () => null, log = console } = {}) {
  const problem = validate(payload);
  if (problem === 'spam') return { ok: true, spam: true };
  if (problem) { const e = new Error(problem); e.status = 400; throw e; }

  const p = { ...payload, email: payload.email.trim().toLowerCase() };
  const formLabel = FORM_LABELS[p.form] || p.form;
  const tags = tagsFor(p);
  const result = { ok: true, tags, mailchimp: false, adminNotified: false, replySent: false };

  result.contact = await saveContact({ ...p, tags });                   // 1. RepShare contact first

  if (env.MAILCHIMP_API_KEY && env.MAILCHIMP_AUDIENCE_ID) {             // 2. Mailchimp
    try {
      const hash = crypto.createHash('md5').update(p.email).digest('hex');
      const base = `/lists/${env.MAILCHIMP_AUDIENCE_ID}/members/${hash}`;
      await mailchimp(env, fetchImpl, 'PUT', base, {
        email_address: p.email,
        status_if_new: p.consent ? 'subscribed' : 'transactional',
        ...(p.consent ? { status: 'subscribed' } : {}),
        merge_fields: Object.fromEntries(Object.entries({ FNAME: p.firstName, LNAME: p.lastName, PHONE: p.mobile, COMPANY: p.company }).filter(([, v]) => v)),
      });
      await mailchimp(env, fetchImpl, 'POST', `${base}/tags`, { tags: tags.map((name) => ({ name, status: 'active' })) });
      await mailchimp(env, fetchImpl, 'POST', `${base}/notes`, { note: `${formLabel}\n` + answersTable(p).map(([k, v]) => `${k}: ${v}`).join('\n') });
      result.mailchimp = true;
    } catch (e) { log.error('[enquiries] Mailchimp:', e.message); }
  }

  if (env.MAILCHIMP_TRANSACTIONAL_KEY) {                                // 3 + 4. instant emails
    const from = env.ENQUIRY_FROM_EMAIL || 'hello@drinksnetwork.com.au';
    const admins = (env.ENQUIRY_ADMIN_EMAILS || DEFAULT_ADMINS.join(',')).split(',').map((s) => s.trim()).filter(Boolean);
    try {
      const a = adminEmail(p, formLabel);
      await transactional(env, fetchImpl, { from_email: from, from_name: 'Drinks Network website', to: admins.map((email) => ({ email, type: 'to' })), subject: a.subject, html: a.html, headers: { 'Reply-To': p.email }, tags: ['admin-new-lead'] });
      result.adminNotified = true;
    } catch (e) { log.error('[enquiries] admin email:', e.message); }
    const links = briefLinks(p, env);
    try {
      const r = replyEmail({ ...p, links: links && p.sendCopy !== false ? links : null }, formLabel);
      await transactional(env, fetchImpl, { from_email: from, from_name: 'Drinks Network', to: [{ email: p.email, name: p.firstName || '' }], subject: r.subject, html: r.html, tags: ['enquiry-reply', `form-${p.form}`] });
      result.replySent = true;
    } catch (e) { log.error('[enquiries] reply email:', e.message); }
    if (links) {
      result.shared = [];
      for (const email of shareList(p)) {
        try {
          const m = shareEmail(p, links);
          await transactional(env, fetchImpl, { from_email: from, from_name: 'Drinks Network', to: [{ email, type: 'to' }], subject: m.subject, html: m.html, headers: { 'Reply-To': p.email }, tags: ['brief-share', `form-${p.form}`] });
          result.shared.push(email);
        } catch (e) { log.error('[enquiries] share email:', e.message); }
      }
    }
  }
  return result;
}

// Express example:
//   import { handleEnquiry } from './server/enquiries.mjs';
//   app.post('/api/enquiries', express.json(), async (req, res) => {
//     try { res.status(201).json(await handleEnquiry(req.body, { saveContact: (c) => db.contacts.upsert(c) })); }
//     catch (e) { res.status(e.status || 500).json({ error: e.status ? e.message : 'Something went wrong' }); }
//   });
