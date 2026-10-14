// node --test server/test  — checks the handler with Mailchimp mocked out.
import test from 'node:test';
import assert from 'node:assert/strict';
import { handleEnquiry } from '../enquiries.mjs';

const env = { MAILCHIMP_API_KEY: 'k-us21', MAILCHIMP_AUDIENCE_ID: 'aud1', MAILCHIMP_TRANSACTIONAL_KEY: 'mk', ENQUIRY_FROM_EMAIL: 'hello@drinksnetwork.com.au' };
function mockFetch() {
  const calls = [];
  const f = async (url, o) => { calls.push({ url, method: o.method, body: o.body ? JSON.parse(o.body) : null }); return { ok: true, status: 200, json: async () => ({}), text: async () => '' }; };
  f.calls = calls; return f;
}
const lead = { form: 'brands-subscription', tags: ['Vendor'], package: 'Roll Out', firstName: 'Sam', email: 'Sam@Brand.com ', mobile: '0400', company: 'Brand Co', cities: ['Brisbane'], consent: { status: 'subscribed' }, website: '', pageUrl: 'https://site/brands' };

test('saves, tags in Mailchimp, notifies admins and replies', async () => {
  const f = mockFetch(); let saved;
  const r = await handleEnquiry(lead, { env, fetchImpl: f, saveContact: async (c) => (saved = c, { id: 7 }) });
  assert.equal(saved.email, 'sam@brand.com');
  assert.deepEqual(r.tags, ['Vendor', 'form:brands-subscription', 'enquiry']);
  assert.ok(r.mailchimp && r.adminNotified && r.replySent);
  const put = f.calls.find((c) => c.method === 'PUT');
  assert.match(put.url, /us21\.api\.mailchimp\.com\/3\.0\/lists\/aud1\/members\/[0-9a-f]{32}$/);
  assert.equal(put.body.status_if_new, 'subscribed');
  const mails = f.calls.filter((c) => c.url.includes('mandrillapp'));
  assert.equal(mails[0].body.message.to.length, 4);
  assert.match(mails[0].body.message.subject, /RepShare subscription request · Brand Co · Roll Out/);
  assert.equal(mails[1].body.message.to[0].email, 'sam@brand.com');
});

test('honeypot is dropped quietly, bad email rejected', async () => {
  const f = mockFetch();
  assert.equal((await handleEnquiry({ ...lead, website: 'x' }, { env, fetchImpl: f })).spam, true);
  assert.equal(f.calls.length, 0);
  await assert.rejects(handleEnquiry({ ...lead, email: 'nope' }, { env, fetchImpl: f }), /valid email/);
});

test('a Mailchimp outage never loses the lead', async () => {
  const f = async () => ({ ok: false, status: 500, text: async () => 'down' });
  let saved = false;
  const r = await handleEnquiry(lead, { env, fetchImpl: f, saveContact: async () => (saved = true), log: { error() {} } });
  assert.ok(saved && r.ok && !r.mailchimp);
});

test('tasting brief: reply carries the brief links and up to 3 shares go out', async () => {
  const f = mockFetch();
  const brief = { form: 'tasting-brief', tags: ['Buyer'], firstName: 'Ana', lastName: 'Lee', email: 'ana@bar.com', mobile: '0400', company: 'Bar', sendCopy: true,
    shareWith: ['boss@bar.com', 'ANA@bar.com', 'bad', 'a@x.com', 'b@x.com', 'c@x.com'], pageUrl: 'https://evil.example/x' };
  const r = await handleEnquiry(brief, { env, fetchImpl: f });
  assert.deepEqual(r.shared, ['boss@bar.com', 'a@x.com', 'b@x.com']);
  const mails = f.calls.filter((c) => c.url.includes('mandrillapp'));
  assert.equal(mails.length, 5);                                     // admins, reply, 3 shares
  assert.match(mails[1].body.message.html, /site\.drinksnetwork\.com\.au\/whisky-adventure\/tasting-series\?brief=open/);
  assert.doesNotMatch(mails[2].body.message.html, /evil\.example/);
  assert.match(mails[2].body.message.subject, /Ana Lee shared the Drinks Network Tasting Series partnership brief/);
});

test('bar takeover pack: reply and shares link to the takeover pack', async () => {
  const f = mockFetch();
  const pack = { form: 'bar-takeover-pack', campaign: 'bar-takeover', tags: ['Vendor'], firstName: 'Sam', lastName: 'Ng', email: 'sam@brand.com', mobile: '0400', company: 'Brand', city: 'Ballarat', sendCopy: true, shareWith: ['ops@brand.com'] };
  const r = await handleEnquiry(pack, { env, fetchImpl: f });
  assert.deepEqual(r.shared, ['ops@brand.com']);
  const mails = f.calls.filter((c) => c.url.includes('mandrillapp'));
  assert.match(mails[1].body.message.html, /\/bar-takeover\?pack=open/);
  assert.match(mails[1].body.message.html, /bar-takeover-pack\.pdf/);
  assert.match(mails[2].body.message.subject, /Sam Ng shared the Drinks Network Bar Takeover partnership pack/);
  assert.match(mails[2].body.message.html, /guest bartender/);
});
