// Tests the sign-in and lock rules in lib/ and worker/ without deploying. Run: npm test
import { build } from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const tmp = path.join(ROOT, '.test-build');
fs.mkdirSync(tmp, { recursive: true });
await build({ entryPoints: { mw: path.join(ROOT, 'lib/guard.js'), me: path.join(ROOT, 'lib/me.js'), worker: path.join(ROOT, 'worker/index.js') },
  bundle: true, format: 'esm', platform: 'neutral', outdir: tmp, logLevel: 'error' });
const mw = await import(path.join(tmp, 'mw.js'));
const me = await import(path.join(tmp, 'me.js'));
const worker = (await import(path.join(tmp, 'worker.js'))).default;
const students = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/students/students.json'), 'utf8'));
const site = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/site.json'), 'utf8'));
const stu = students[0];
const ADMIN = site.admins[0];

const realNow = Date.now;
const setNow = iso => { Date.now = () => new Date(iso).getTime(); };
const OK = new Response('ok', { status: 200 });
async function hit(p, env = {}, headers = {}) {
  const ctx = { request: new Request('https://x.pages.dev' + p, { headers }), env, data: {}, next: async () => new Response('ok', { status: 200 }) };
  return mw.onRequest(ctx);
}
let passed = 0;
const t = async (name, fn) => { await fn(); passed++; console.log('  ok  ' + name); };

// 1. Not set up yet
await t('no sign-in configured shows the setup page', async () => assert.equal((await hit('/')).status, 503));

// 2. Student rules with DEV_EMAIL (preview mode)
const sEnv = { DEV_EMAIL: stu.emails[0] };
await t('enrolled student can open home', async () => assert.equal((await hit('/', sEnv)).status, 200));
await t('unknown email is refused', async () => assert.equal((await hit('/', { DEV_EMAIL: 'nobody@x.com' })).status, 403));
setNow('2026-11-08T12:00:00-05:00');
await t('week 1 locked on Sun 8 Nov (opens Mon 9 Nov)', async () => assert.equal((await hit('/weeks/week-01/', sEnv)).status, 403));
setNow('2026-11-09T00:30:00-05:00');
await t('week 1 open on Mon 9 Nov', async () => assert.equal((await hit('/weeks/week-01/', sEnv)).status, 200));
await t('week 2 still locked on 9 Nov', async () => assert.equal((await hit('/weeks/week-02/', sEnv)).status, 403));
await t('week 1 solutions locked until after class', async () => assert.equal((await hit('/weeks/week-01/solutions/a.ino', sEnv)).status, 403));
setNow('2026-11-21T09:00:00-05:00');
await t('week 1 solutions open Sat 21 Nov', async () => assert.equal((await hit('/weeks/week-01/solutions/a.ino', sEnv)).status, 200));
await t('own student page opens', async () => assert.equal((await hit(`/students/${stu.slug}/`, sEnv)).status, 200));
await t('another student page is refused', async () => assert.equal((await hit('/students/someone-else/', sEnv)).status, 403));
await t('student list is refused', async () => assert.equal((await hit('/students/', sEnv)).status, 403));
await t('/me redirects to own page', async () => { const r = await hit('/me', sEnv); assert.equal(r.status, 302); assert.match(r.headers.get('location'), new RegExp(`/students/${stu.slug}/$`)); });

// 3. Admin sees everything
const aEnv = { DEV_EMAIL: ADMIN };
setNow('2026-10-14T12:00:00+05:30');
await t('admin opens week 12 early', async () => assert.equal((await hit('/weeks/week-12/', aEnv)).status, 200));
await t('admin opens any student page', async () => assert.equal((await hit(`/students/${stu.slug}/`, aEnv)).status, 200));

// 4. Real Cloudflare Access tokens
const kp = await crypto.subtle.generateKey({ name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }, true, ['sign', 'verify']);
const jwk = { ...(await crypto.subtle.exportKey('jwk', kp.publicKey)), kid: 'k1' };
const b64u = b => Buffer.from(b).toString('base64url');
async function token(payload) {
  const h = b64u(JSON.stringify({ alg: 'RS256', kid: 'k1' })), p = b64u(JSON.stringify(payload));
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', kp.privateKey, new TextEncoder().encode(`${h}.${p}`));
  return `${h}.${p}.${b64u(sig)}`;
}
const realFetch = globalThis.fetch;
globalThis.fetch = async u => String(u).endsWith('/cdn-cgi/access/certs') ? new Response(JSON.stringify({ keys: [jwk] })) : realFetch(u);
Date.now = realNow;
const xEnv = { ACCESS_AUD: 'aud123', ACCESS_TEAM_DOMAIN: 'sterling.cloudflareaccess.com' };
const good = await token({ aud: ['aud123'], iss: 'https://sterling.cloudflareaccess.com', exp: Math.floor(Date.now() / 1000) + 600, email: ADMIN });
await t('valid Access token signs in', async () => assert.equal((await hit('/', xEnv, { 'cf-access-jwt-assertion': good })).status, 200));
await t('valid token in cookie signs in', async () => assert.equal((await hit('/', xEnv, { cookie: `CF_Authorization=${good}` })).status, 200));
const wrongAud = await token({ aud: ['other'], iss: 'https://sterling.cloudflareaccess.com', exp: Math.floor(Date.now() / 1000) + 600, email: ADMIN });
await t('token for another app is refused', async () => assert.equal((await hit('/', xEnv, { 'cf-access-jwt-assertion': wrongAud })).status, 401));
const expired = await token({ aud: ['aud123'], iss: 'https://sterling.cloudflareaccess.com', exp: Math.floor(Date.now() / 1000) - 10, email: ADMIN });
await t('expired token is refused', async () => assert.equal((await hit('/', xEnv, { 'cf-access-jwt-assertion': expired })).status, 401));
const tampered = good.slice(0, -4) + 'AAAA';
await t('tampered token is refused', async () => assert.equal((await hit('/', xEnv, { 'cf-access-jwt-assertion': tampered })).status, 401));
await t('team domain pasted with https:// still works', async () => assert.equal((await hit('/', { ...xEnv, ACCESS_TEAM_DOMAIN: 'https://sterling.cloudflareaccess.com/' }, { 'cf-access-jwt-assertion': good })).status, 200));
await t('without ACCESS_AUD, a valid team token signs in', async () => assert.equal((await hit('/', { ACCESS_TEAM_DOMAIN: 'sterling.cloudflareaccess.com' }, { 'cf-access-jwt-assertion': wrongAud })).status, 200));
const otherTeam = await token({ aud: ['aud123'], iss: 'https://evil.cloudflareaccess.com', exp: Math.floor(Date.now() / 1000) + 600, email: ADMIN });
await t('a token from another team is refused', async () => assert.equal((await hit('/', { ACCESS_TEAM_DOMAIN: 'sterling.cloudflareaccess.com' }, { 'cf-access-jwt-assertion': otherTeam })).status, 401));
await t('a faked email header alone is refused', async () => assert.equal((await hit('/', xEnv, { 'cf-access-authenticated-user-email': ADMIN })).status, 401));

// 5. Home page data
const weeksJson = fs.readFileSync(path.join(ROOT, 'dist/data/weeks.json'), 'utf8');
setNow('2026-11-10T12:00:00-05:00');
const r = await me.onRequestGet({ request: new Request('https://x.pages.dev/api/me'), env: { ASSETS: { fetch: async () => new Response(weeksJson) } }, data: { who: { name: stu.name, admin: false, student: stu } } });
const j = await r.json();
await t('/api/me: week 1 open, week 2 locked, next class is week 1 on 15 Nov', async () => {
  assert.equal(j.weeks[0].unlocked, true); assert.equal(j.weeks[1].unlocked, false);
  assert.equal(j.next, 1); assert.equal(j.weeks[0].classDate, '2026-11-15'); assert.equal(j.weeks[11].classDate, '2027-01-31');
  assert.equal(j.weeks[1].unlockDate, '2026-11-16');
});

// 6. Whole Worker: assets only served after the checks pass
Date.now = realNow;
const served = [];
const wEnv = { ...xEnv, ASSETS: { fetch: async req => { served.push(new URL(req.url).pathname); return new URL(req.url).pathname === '/data/weeks.json' ? new Response(weeksJson) : new Response('page'); } } };
await t('worker refuses a request with no sign-in and serves nothing', async () => { served.length = 0; const r = await worker.fetch(new Request('https://x.workers.dev/weeks/week-01/'), wEnv); assert.equal(r.status, 401); assert.equal(served.length, 0); });
await t('worker serves a page after a valid sign-in', async () => { const r = await worker.fetch(new Request('https://x.workers.dev/', { headers: { 'cf-access-jwt-assertion': good } }), wEnv); assert.equal(r.status, 200); assert.equal(await r.text(), 'page'); });
await t('worker answers /api/me after sign-in', async () => { const r = await worker.fetch(new Request('https://x.workers.dev/api/me', { headers: { 'cf-access-jwt-assertion': good } }), wEnv); assert.equal(r.status, 200); assert.equal((await r.json()).admin, true); });

Date.now = realNow; globalThis.fetch = realFetch;
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`\n${passed} checks passed`);
