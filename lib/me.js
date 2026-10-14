// Home page data for the signed-in person: their cohort, class dates and which weeks are open.
import { site, schedule, weekTimes } from './course.js';

export async function onRequestGet({ request, env, data }) {
  const who = data.who;
  const url = new URL(request.url);
  const cohort = who.admin ? (url.searchParams.get('cohort') || Object.keys(schedule.cohorts)[0]) : who.student.cohort;
  let weeks = [];
  try { weeks = await (await env.ASSETS.fetch(new URL('/data/weeks.json', url))).json(); } catch (_) {}
  const now = Date.now();
  const list = weeks.map(w => {
    const t = weekTimes(cohort, w.n);
    return { ...w, classDate: t.classDate, unlocked: who.admin || now >= t.unlock.getTime(), unlockDate: new Date(t.unlock.getTime() + 43200000).toISOString().slice(0, 10) };
  });
  const today = new Date(now - 5 * 3600000).toISOString().slice(0, 10);
  const next = list.find(w => w.classDate >= today) || null;
  return Response.json({
    name: who.name, admin: who.admin, slug: who.student ? who.student.slug : null,
    cohort, cohortLabel: (schedule.cohorts[cohort] || {}).label || cohort,
    cohorts: who.admin ? Object.entries(schedule.cohorts).map(([k, v]) => ({ key: k, label: v.label })) : undefined,
    site: { classDay: site.classDay, classTime: site.classTime, meetLink: site.meetLink, homeworkForm: site.homeworkForm,
      oneOnOneLink: site.oneOnOneLink, whatsapp: site.whatsapp, whatsappLink: site.whatsappLink },
    weeks: list, next: next ? next.n : null,
  }, { headers: { 'cache-control': 'private, no-store' } });
}
