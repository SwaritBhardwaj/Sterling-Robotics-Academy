// Shared logic for the Worker: who is signed in, and which weeks they can open.
import site from '../content/site.json';
import schedule from '../content/schedule.json';
import students from '../content/students/students.json';

export { site, schedule, students };

const DAY = 86400000;

const cookieOf = (request, name) => { const m = (request.headers.get('cookie') || '').match(new RegExp(`(?:^|; )${name}=([^;]+)`)); return m ? decodeURIComponent(m[1]) : null; };

/**
 * The time the rules use. Normally the real time. Only on a preview Worker (PREVIEW_CLOCK=1, which the
 * live site never sets) can a `sim_date` cookie pretend it is another day, to show how weeks open.
 */
export function clock(request, env) {
  if (env && env.PREVIEW_CLOCK === '1' && !teamDomain(env) && request) {
    const d = cookieOf(request, 'sim_date');
    if (d && /^\d{4}-\d{2}-\d{2}$/.test(d)) return new Date(`${d}T09:00:00${schedule.timezoneOffset || '-05:00'}`).getTime();
  }
  return Date.now();
}

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
    cls,
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
    if (env.ACCESS_AUD && !aud.includes(env.ACCESS_AUD)) return null;
    if (payload.iss !== `https://${teamDomain(env)}`) return null;
    if (!payload.exp || payload.exp * 1000 < Date.now()) return null;
    const jwk = (await accessKeys(teamDomain(env), fetcher)).find(k => k.kid === header.kid);
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

/** Team domain without https:// or a trailing slash, however it was pasted. */
export function teamDomain(env) {
  return String(env.ACCESS_TEAM_DOMAIN || '').trim().replace(/^https?:\/\//, '').replace(/\/+$/, '');
}

/**
 * Who is making this request. With ACCESS_TEAM_DOMAIN set, only a valid Cloudflare Access
 * token signed for that team counts. ACCESS_AUD (optional) also pins it to this one app.
 * DEV_EMAIL is for local testing only. Returns { email } or { error: 'setup' | 'signin' }.
 */
export async function identify(request, env, fetcher = fetch) {
  if (teamDomain(env)) {
    const token = request.headers.get('cf-access-jwt-assertion') || cookie(request, 'CF_Authorization');
    const email = token ? await verifyAccessJwt(token, env, fetcher) : null;
    return email ? { email } : { error: 'signin' };
  }
  if (env.DEV_EMAIL) {
    // Preview Workers only: switch between the sample student and Swarit's view.
    if (env.PREVIEW_CLOCK === '1') {
      const as = cookieOf(request, 'sim_as');
      if (as === 'admin' && site.admins && site.admins[0]) return { email: site.admins[0].toLowerCase() };
      if (as === 'student' && students[0]) return { email: students[0].emails[0].toLowerCase() };
    }
    return { email: env.DEV_EMAIL.toLowerCase() };
  }
  return { error: 'setup' };
}
