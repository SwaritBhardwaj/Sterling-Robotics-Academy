// Weeks written in the new format (header `format: 2`): short resources that end in a quick quiz,
// then the assignment as small tasks with paid hints. Quiz answers and hints live in the week's
// private/ folder. They are never written to the public site: they go into build/.generated/private.json,
// which only the Worker reads (lib/platform.js).
import fs from 'node:fs';
import path from 'node:path';

const pad = n => String(n).padStart(2, '0');

/** Splits "## Name" sections of a private file into { slug: [line, ...] } using numbered lines. */
function numberedSections(file) {
  const out = {};
  if (!fs.existsSync(file)) return out;
  let cur = null;
  for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
    const h = line.match(/^##\s+(\S+)/);
    if (h) { cur = out[h[1]] = []; continue; }
    const m = line.match(/^\d+\.\s+(.+)$/);
    if (cur && m) cur.push(m[1].trim());
  }
  return out;
}

/** Pulls the "## Quick quiz" block off a resource body: questions with lettered options. */
function splitQuiz(body) {
  const i = body.search(/^##\s+Quick quiz\s*$/m);
  if (i < 0) return { body, quiz: [] };
  const quiz = [];
  for (const line of body.slice(i).split('\n').slice(1)) {
    const q = line.match(/^\d+\.\s+(.+)$/);
    const o = line.match(/^\s+-\s+(.+)$/);
    if (q) quiz.push({ q: q[1].trim(), options: [] });
    else if (o && quiz.length) quiz[quiz.length - 1].options.push(o[1].trim());
  }
  return { body: body.slice(0, i), quiz };
}

/** Reads one format-2 week folder into resources, tasks and the private answers and hints. */
export function loadWeek(dir, n, read) {
  const list = sub => (fs.existsSync(path.join(dir, sub)) ? fs.readdirSync(path.join(dir, sub)).filter(f => /^\d{2}-.+\.md$/.test(f)).sort() : []);
  const resources = list('resources').map((f, i) => {
    const { meta, body } = read(path.join(dir, 'resources', f));
    const slug = f.replace(/\.md$/, '');
    const { body: rest, quiz } = splitQuiz(body);
    return { id: `w${pad(n)}-r${pad(i + 1)}`, slug, n: i + 1, meta, body: rest, quiz };
  });
  const tasks = list('tasks').map((f, i) => {
    const { meta, body } = read(path.join(dir, 'tasks', f));
    return { id: `w${pad(n)}-t${pad(i + 1)}`, slug: f.replace(/\.md$/, ''), n: i + 1, meta, body };
  });
  const ans = numberedSections(path.join(dir, 'private', 'answers.md'));
  const hin = numberedSections(path.join(dir, 'private', 'hints.md'));
  const answers = {}, hints = {};
  for (const r of resources) {
    const rows = ans[r.slug] || [];
    if (rows.length !== r.quiz.length) throw new Error(`week ${n} ${r.slug}: ${r.quiz.length} quiz questions but ${rows.length} answers`);
    answers[r.id] = rows.map((row, qi) => {
      const [a, why = ''] = row.split('|').map(s => s.trim());
      const k = a.toUpperCase().charCodeAt(0) - 65;
      if (!(k >= 0 && k < r.quiz[qi].options.length)) throw new Error(`week ${n} ${r.slug} question ${qi + 1}: answer "${a}" is not an option`);
      return { a: a.toUpperCase(), why };
    });
  }
  for (const t of tasks) (hin[t.slug] || []).slice(0, 3).forEach((h, i) => { hints[`${t.id}-h${i + 1}`] = h; });
  return { resources, tasks, answers, hints };
}

const KIND = { must: 'must do', stretch: 'stretch', optional: 'optional', bonus: 'bonus' };
const HINT_NAMES = ['a nudge', 'the approach', 'nearly the answer'];

/**
 * Writes the week page, one page per resource and one per task.
 * h: helpers from build.mjs (md, esc, layout, write, videoBlock, youtubeId), plus the week, its
 * neighbours and the shared blocks (recording, files, solutions) already built for it.
 */
export function writeWeek(h, { w, weeks, i, data, recording, filesBlock, solBlock, questionHtml, introHtml, costs }) {
  const { esc, layout, write, md } = h;
  const base = w.url;
  const fixImg = html => html.replace(/(src|href)="img\//g, `$1="${base}img/`);
  const margin = extra => `<aside class="margin">
    <p class="wk" aria-label="Week ${w.n} of ${weeks.length}">week <b>${w.n}</b> <span>of ${weeks.length}</span></p>
    ${extra}
  </aside>`;
  const prevW = weeks[i - 1], nextW = weeks[i + 1];

  const resRows = data.resources.map(r => `<li data-res="${r.id}"><a href="${base}r/${r.slug}/"><span class="n">${r.n}</span><span class="t">${esc(r.meta.title)}</span><span class="d" data-state="${r.id}">${esc(r.meta.minutes || '')} min ${r.meta.type === 'video' ? 'video' : 'read'}</span></a></li>`).join('');
  const taskRows = data.tasks.map(t => `<li data-task="${t.id}" class="k-${esc(t.meta.kind || 'must')}"><a href="${base}t/${t.slug}/"><span class="n">${t.n}</span><span class="t">${esc(t.meta.title)}</span><span class="d" data-state="${t.id}">${esc(KIND[t.meta.kind] || 'must do')}</span></a></li>`).join('');

  write(`weeks/${w.dir}/index.html`, layout({
    title: `Week ${w.n}: ${w.meta.title}`, active: 'weeks', bodyClass: 'week v2',
    body: `${margin(`<p class="note" data-week-date="${w.n}"></p><p class="note">${esc(w.meta.kit || '')}</p>`)}
  <article class="col prose" data-week="${w.n}">
    <h1>${esc(w.meta.title)}</h1>
    ${questionHtml ? `<p class="question">${questionHtml}</p>` : ''}
    <p class="todo"><mark class="sweep" data-next-step="${w.n}">Start with the first page below.</mark></p>
    ${fixImg(introHtml)}
    <section class="steps-block"><h2>Read first</h2><p class="aside-note">Each page ends with a quick quiz. Pass it to earn Volts.</p><ol class="contents steps">${resRows}</ol></section>
    <section class="steps-block"><h2>Then do</h2><p class="aside-note">One small step at a time. Submit each task on its own page.</p><ol class="contents steps">${taskRows}</ol></section>
    ${recording}
    ${filesBlock}${solBlock}
    <nav class="pager" aria-label="Weeks">${prevW ? `<a href="${prevW.url}" rel="prev"><span>previous</span>Week ${prevW.n}: ${esc(prevW.meta.title)}</a>` : '<span></span>'}${nextW ? `<a href="${nextW.url}" rel="next"><span>next</span>Week ${nextW.n}: ${esc(nextW.meta.title)}</a>` : '<span></span>'}</nav>
  </article>`,
  }));

  data.resources.forEach((r, k) => {
    const yt = h.youtubeId(r.meta.video);
    const video = r.meta.type === 'video'
      ? (yt ? h.videoBlock(yt, r.meta.title) : `<figure class="taped video-slot"><div class="video placeholder"><p>Swarit's video goes here.</p></div><figcaption>${esc(r.meta.title)}</figcaption></figure>`)
      : '';
    const quiz = r.quiz.length ? `<form class="quiz" data-quiz="${r.id}" novalidate>
      <h2>Quick quiz</h2>
      <p class="aside-note">Pass to earn <b>${costs.quizFirst} Volts</b> (${costs.quizRetry} on a second try).</p>
      ${r.quiz.map((q, qi) => `<fieldset class="q" data-q="${qi + 1}"><legend><span class="qn">${qi + 1}</span>${esc(q.q)}</legend>
        ${q.options.map((o, oi) => `<label><input type="radio" name="q${qi + 1}" value="${String.fromCharCode(65 + oi)}"><span>${esc(o)}</span></label>`).join('')}
        <p class="why" hidden></p></fieldset>`).join('')}
      <p class="quiz-actions"><button class="btn" type="submit">Check my answers</button></p>
      <p class="quiz-result" role="status" aria-live="polite"></p>
    </form>` : '';
    const prev = data.resources[k - 1], next = data.resources[k + 1];
    const nextLink = next ? `<a href="${base}r/${next.slug}/" rel="next"><span>next page</span>${esc(next.meta.title)}</a>`
      : data.tasks[0] ? `<a href="${base}t/${data.tasks[0].slug}/" rel="next"><span>now do</span>${esc(data.tasks[0].meta.title)}</a>` : '<span></span>';
    write(`weeks/${w.dir}/r/${r.slug}/index.html`, layout({
      title: `${r.meta.title} · Week ${w.n}`, active: 'weeks', bodyClass: 'week v2 resource',
      body: `${margin(`<p class="note">page ${r.n} of ${data.resources.length}<br>${esc(r.meta.minutes || '')} min ${r.meta.type === 'video' ? 'video' : 'read'}</p><p class="note"><a href="${base}">back to week ${w.n}</a></p>`)}
  <article class="col prose" data-res-page="${r.id}" data-week="${w.n}">
    <p class="crumb"><a href="${base}">Week ${w.n}</a> · Read first</p>
    <h1>${esc(r.meta.title)}</h1>
    ${video}
    ${fixImg(md(r.body))}
    ${quiz}
    <nav class="pager" aria-label="Pages">${prev ? `<a href="${base}r/${prev.slug}/" rel="prev"><span>previous page</span>${esc(prev.meta.title)}</a>` : `<a href="${base}" rel="prev"><span>back to</span>Week ${w.n}</a>`}${nextLink}</nav>
  </article>`,
    }));
  });

  data.tasks.forEach((t, k) => {
    const kind = t.meta.kind || 'must';
    const sub = t.meta.submit || 'text';
    const hintIds = Object.keys(data.hints).filter(id => id.startsWith(`${t.id}-h`));
    const hints = hintIds.length ? `<section class="hints" data-hints="${t.id}"><h2>Stuck?</h2>
      <p class="aside-note">Hints cost Volts. Once opened, a hint stays open. <span data-free-from="${w.n}"></span></p>
      <ol class="hintlist">${hintIds.map((id, hi) => `<li data-hint="${id}" data-cost="${costs.hints[hi]}"><button type="button" class="hintbtn"><span>Hint ${hi + 1}: ${HINT_NAMES[hi]}</span><span class="cost">${costs.hints[hi]} Volts</span></button><div class="hinttext" hidden></div></li>`).join('')}</ol>
    </section>` : '';
    const prev = data.tasks[k - 1], next = data.tasks[k + 1];
    write(`weeks/${w.dir}/t/${t.slug}/index.html`, layout({
      title: `${t.meta.title} · Week ${w.n}`, active: 'weeks', bodyClass: 'week v2 taskpage',
      body: `${margin(`<p class="note">task ${t.n} of ${data.tasks.length}</p><p class="tag k-${esc(kind)}">${esc(KIND[kind] || kind)}</p><p class="note"><a href="${base}">back to week ${w.n}</a></p>`)}
  <article class="col prose" data-task-page="${t.id}" data-week="${w.n}">
    <p class="crumb"><a href="${base}">Week ${w.n}</a> · Then do</p>
    <h1>${esc(t.meta.title)}</h1>
    ${fixImg(md(t.body))}
    ${hints}
    <section class="submitbox"><h2>Submit</h2>
      <form data-submit-task="${t.id}" data-kind="${esc(sub)}" novalidate>
        ${sub !== 'link' ? `<label class="field"><span>Your work</span><textarea name="body" rows="8" placeholder="Paste your filled-in table, code or answers here"></textarea></label>` : ''}
        ${sub !== 'text' ? `<label class="field"><span>Link</span><input type="url" name="link" inputmode="url" placeholder="https://"></label>` : ''}
        ${sub === 'link' ? `<label class="field"><span>Note (optional)</span><textarea name="body" rows="3" placeholder="Your guess, what happened, anything Swarit should know"></textarea></label>` : ''}
        <p class="quiz-actions"><button class="btn" type="submit">Submit task</button></p>
        <p class="submit-status" role="status" aria-live="polite"></p>
      </form>
      <div class="feedback" hidden></div>
    </section>
    <nav class="pager" aria-label="Tasks">${prev ? `<a href="${base}t/${prev.slug}/" rel="prev"><span>previous task</span>${esc(prev.meta.title)}</a>` : `<a href="${base}" rel="prev"><span>back to</span>Week ${w.n}</a>`}${next ? `<a href="${base}t/${next.slug}/" rel="next"><span>next task</span>${esc(next.meta.title)}</a>` : `<a href="${base}" rel="next"><span>back to</span>Week ${w.n}</a>`}</nav>
  </article>`,
    }));
  });

  // Public outline for the browser: ids, titles and links only. No answers, no hints.
  return {
    n: w.n,
    resources: data.resources.map(r => ({ id: r.id, title: r.meta.title, url: `${base}r/${r.slug}/` })),
    tasks: data.tasks.map(t => ({ id: t.id, title: t.meta.title, url: `${base}t/${t.slug}/`, kind: t.meta.kind || 'must' })),
  };
}
