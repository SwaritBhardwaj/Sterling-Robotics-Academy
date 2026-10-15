// Quiz checks and hints for new-format weeks. Answers and hints are bundled into the Worker at build
// time (build/.generated/private.json) and never served as files. Each answer is checked here, and a
// hint is sent only for an open week.
//
// Prototype note: Volts, submissions and reviews are kept in the browser for the preview. The real
// version stores them in D1 and checks the Volts balance here before sending a hint (PRD v2.2).
import priv from '../build/.generated/private.json';
import { weekTimes, clock } from './course.js';

const json = (body, status = 200) => Response.json(body, { status, headers: { 'cache-control': 'private, no-store' } });

/** Writes must come from this site, as JSON. Stops other sites posting on a signed-in student's behalf. */
function sameSite(request) {
  const origin = request.headers.get('origin');
  const ok = !origin || origin === new URL(request.url).origin;
  return ok && (request.headers.get('content-type') || '').includes('application/json');
}

function weekOpen(who, id, request, env) {
  const n = Number((id.match(/^w(\d{2})-/) || [])[1]);
  if (!n) return { ok: false, n };
  if (who.admin) return { ok: true, n, free: true };
  const t = weekTimes(who.student.cohort, n), now = clock(request, env);
  return { ok: now >= t.unlock.getTime(), n, free: now >= t.solutions.getTime() };
}

export async function onPost({ request, env, data }, path) {
  if (!sameSite(request)) return json({ error: 'bad request' }, 400);
  let body;
  try { body = await request.json(); } catch (_) { return json({ error: 'bad request' }, 422); }

  if (path === '/api/quiz') {
    const id = String(body.resource || '');
    const key = priv.answers[id];
    if (!key) return json({ error: 'not found' }, 404);
    if (!weekOpen(data.who, id, request, env).ok) return json({ error: 'locked' }, 403);
    const given = body.answers && typeof body.answers === 'object' ? body.answers : {};
    const wrong = key.map((k, i) => (String(given[i + 1] || '').toUpperCase() === k.a ? null : { q: i + 1, why: k.why })).filter(Boolean);
    return json({ pass: wrong.length === 0, wrong });
  }

  if (path === '/api/hint') {
    const id = String(body.hint || '');
    const text = priv.hints[id];
    if (!text) return json({ error: 'not found' }, 404);
    const w = weekOpen(data.who, id, request, env);
    if (!w.ok) return json({ error: 'locked' }, 403);
    return json({ text, free: !!w.free });
  }

  return json({ error: 'not found' }, 404);
}
