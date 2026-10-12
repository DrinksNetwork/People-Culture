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
