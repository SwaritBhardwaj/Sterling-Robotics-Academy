// Runs before every page. Checks sign-in, enrolment, week unlock dates and private student pages.
import { identify, whoIs, weekTimes, unlockDate, site } from '../lib/course.js';

const PUBLIC = [/^\/assets\//, /^\/favicon\.svg$/, /^\/robots\.txt$/];

function page(status, title, msg) {
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title} · Sterling</title><link rel="stylesheet" href="/assets/site.css"></head>
<body><main class="wrap narrow msgpage"><a class="brand" href="/"><b>Sterling</b><span>ROBOTICS ACADEMY</span></a><h1>${title}</h1><p>${msg}</p>
<p class="muted">WhatsApp ${site.whatsapp} · ${site.email}</p></main></body></html>`;
  return new Response(html, { status, headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' } });
}
const fmt = d => new Date(`${d}T12:00:00Z`).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;
  if (PUBLIC.some(r => r.test(path))) return next();

  const id = await identify(request, env);
  if (id.error === 'setup') return page(503, 'Almost ready', 'Sign-in for this site is not switched on yet.');
  if (id.error) return page(401, 'Please sign in', 'Your sign-in has expired. Reload the page to get a new code by email.');
  const who = whoIs(id.email);
  if (!who) return page(403, 'Not on the class list', `${id.email} is not enrolled. If you joined with a different email, sign in with that one, or message Swarit to add this email.`);
  context.data.who = who;

  if (path === '/me' || path === '/me/') {
    return Response.redirect(new URL(who.admin ? '/students/' : `/students/${who.student.slug}/`, url), 302);
  }

  if (!who.admin) {
    const wk = path.match(/^\/weeks\/week-(\d{2})(\/.*)?$/);
    if (wk) {
      const n = Number(wk[1]), t = weekTimes(who.student.cohort, n), now = Date.now();
      if (now < t.unlock.getTime()) return page(403, `Week ${n} opens soon`, `This week opens on ${fmt(unlockDate(who.student.cohort, n))}.`);
      if (/^\/solutions(\/|$)/.test(wk[2] || '') && now < t.solutions.getTime()) return page(403, 'Solutions open after class', `Week ${n} solutions open the Saturday after class.`);
    }
    const st = path.match(/^\/students(?:\/([^/]+))?/);
    if (st && st[1] !== who.student.slug) return page(403, 'This page is private', 'You can only open your own page. Use My page in the menu.');
  }

  const res = await next();
  const out = new Response(res.body, res);
  out.headers.set('cache-control', 'private, no-store');
  return out;
}
