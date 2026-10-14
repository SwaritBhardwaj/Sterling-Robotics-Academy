// Shared logic for the Pages Functions: who is signed in, and which weeks they can open.
import site from '../content/site.json';
import schedule from '../content/schedule.json';
import students from '../content/students/students.json';

export { site, schedule, students };

const DAY = 86400000;

/** Midnight (course time zone) of a YYYY-MM-DD date, as a Date. */
function at(dateStr) { return new Date(`${dateStr}T00:00:00${schedule.timezoneOffset || '-05:00'}`); }
function ymd(d) { return new Date(d.getTime() - offsetMs()).toISOString().slice(0, 10); }
function offsetMs() {
  const m = /([+-])(\d{2}):(\d{2})/.exec(schedule.timezoneOffset || '-05:00');
  const v = (Number(m[2]) * 60 + Number(m[3])) * 60000;
  return m[1] === '-' ? v : -v;
}

/** Class date, unlock time and solutions time for week n of a cohort. */
export function weekTimes(cohortKey, n) {
  const c = schedule.cohorts[cohortKey] || Object.values(schedule.cohorts)[0];
  const cls = new Date(at(c.firstClass).getTime() + (n - 1) * 7 * DAY);
  return {
    classDate: ymd(cls),
    unlock: new Date(cls.getTime() - (schedule.unlockDaysBeforeClass ?? 6) * DAY),
    solutions: new Date(cls.getTime() + (schedule.solutionsUnlockDaysAfterClass ?? 6) * DAY),
  };
}
export const unlockDate = (cohortKey, n) => ymd(weekTimes(cohortKey, n).unlock);

/** Find the person behind an email: an admin, an enrolled student, or nobody. */
export function whoIs(email) {
  if (!email) return null;
  const e = email.trim().toLowerCase();
  if ((site.admins || []).map(a => a.toLowerCase()).includes(e)) return { email: e, admin: true, name: site.mentor || 'Admin' };
  const s = students.find(st => (st.emails || []).map(a => a.toLowerCase()).includes(e));
  return s ? { email: e, admin: false, name: s.name, student: s } : null;
}

/* ---------- Cloudflare Access sign-in ---------- */
const b64u = s => s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4);
const b64uBytes = s => Uint8Array.from(atob(b64u(s)), c => c.charCodeAt(0));
const b64uJSON = s => JSON.parse(new TextDecoder().decode(b64uBytes(s)));
let certCache = { at: 0, keys: [] };

async function accessKeys(team, fetcher) {
  if (Date.now() - certCache.at < 3600000 && certCache.keys.length) return certCache.keys;
  const r = await fetcher(`https://${team}/cdn-cgi/access/certs`);
  const j = await r.json();
  certCache = { at: Date.now(), keys: j.keys || [] };
  return certCache.keys;
}

/** Checks the Access token's signature, audience, issuer and expiry. Returns the email or null. */
export async function verifyAccessJwt(token, env, fetcher = fetch) {
  try {
    const [h, p, s] = token.split('.');
    const header = b64uJSON(h), payload = b64uJSON(p);
    const aud = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
    if (!aud.includes(env.ACCESS_AUD)) return null;
    if (payload.iss !== `https://${env.ACCESS_TEAM_DOMAIN}`) return null;
    if (!payload.exp || payload.exp * 1000 < Date.now()) return null;
    const jwk = (await accessKeys(env.ACCESS_TEAM_DOMAIN, fetcher)).find(k => k.kid === header.kid);
    if (!jwk) return null;
    const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
    const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64uBytes(s), new TextEncoder().encode(`${h}.${p}`));
    return ok && payload.email ? String(payload.email).toLowerCase() : null;
  } catch (_) { return null; }
}

function cookie(request, name) {
  const m = (request.headers.get('cookie') || '').match(new RegExp(`(?:^|; )${name}=([^;]+)`));
  return m ? m[1] : null;
}

/**
 * Who is making this request. With ACCESS_AUD and ACCESS_TEAM_DOMAIN set, only a valid
 * Cloudflare Access token counts. DEV_EMAIL is for preview testing only.
 * Returns { email } or { error: 'setup' | 'signin' }.
 */
export async function identify(request, env, fetcher = fetch) {
  if (env.ACCESS_AUD && env.ACCESS_TEAM_DOMAIN) {
    const token = request.headers.get('cf-access-jwt-assertion') || cookie(request, 'CF_Authorization');
    const email = token ? await verifyAccessJwt(token, env, fetcher) : null;
    return email ? { email } : { error: 'signin' };
  }
  if (env.DEV_EMAIL) return { email: env.DEV_EMAIL.toLowerCase() };
  return { error: 'setup' };
}
