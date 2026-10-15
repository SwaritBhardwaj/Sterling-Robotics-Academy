// Builds the course site from content/ into dist/.
// Run: npm run build. Cloudflare runs this on every push to main.
// PREVIEW=1 npm run build writes a self-contained design preview (relative links, sample data) instead.
import fs from 'node:fs';
import path from 'node:path';
import { marked } from 'marked';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const C = p => path.join(ROOT, 'content', p);
const PREVIEW = process.env.PREVIEW === '1';
const OUT = path.join(ROOT, PREVIEW ? 'preview' : 'dist');
const site = JSON.parse(fs.readFileSync(C('site.json'), 'utf8'));
const schedule = JSON.parse(fs.readFileSync(C('schedule.json'), 'utf8'));
const students = JSON.parse(fs.readFileSync(C('students/students.json'), 'utf8'));

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

/* ---------- helpers ---------- */
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function read(file) {
  const raw = fs.readFileSync(file, 'utf8');
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?/);
  const meta = {};
  if (m) for (const line of m[1].split('\n')) { const i = line.indexOf(':'); if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim(); }
  return { meta, body: m ? raw.slice(m[0].length) : raw };
}
/** In preview mode, root links become relative so the pages work from any folder. */
function relativise(rel, html) {
  const depth = rel.split('/').length - 1;
  const up = depth ? '../'.repeat(depth) : './';
  return html.replace(/(href|src)="\/(?!\/)([^"]*)"/g, (_, a, p) => {
    let t = p.split('#')[0];
    if (t === '' || t.endsWith('/')) t += 'index.html';
    else if (t === 'me') t = 'students/sample-student/index.html';
    return `${a}="${up}${t}"`;
  });
}
function write(rel, html) {
  const f = path.join(OUT, rel);
  fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, PREVIEW && rel.endsWith('.html') ? relativise(rel, html) : html);
}
function copyDir(src, dst, skip = () => false) {
  if (!fs.existsSync(src)) return;
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name), d = path.join(dst, e.name);
    if (skip(e, s)) continue;
    if (e.isDirectory()) copyDir(s, d, skip);
    else { fs.mkdirSync(dst, { recursive: true }); fs.copyFileSync(s, d); }
  }
}
const size = b => b > 1048576 ? `${(b / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1024))} KB`;
function youtubeId(u) { const m = String(u || '').match(/(?:youtu\.be\/|v=|embed\/|shorts\/)([\w-]{11})/); return m ? m[1] : null; }

function videoBlock(id, title) {
  if (PREVIEW) return `<figure class="taped video-slot"><div class="video placeholder"><p>Video plays here on the live site.</p></div><figcaption>${esc(title)}</figcaption></figure>`;
  return `<figure class="taped"><div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${id}" title="${esc(title)}" allow="accelerometer; encrypted-media; picture-in-picture; fullscreen" allowfullscreen loading="lazy"></iframe></div><figcaption>${esc(title)}</figcaption></figure>`;
}

/**
 * Markdown to HTML, plus the notebook touches:
 * ==text== highlights, a lone image becomes a taped-in figure (alt text is the caption),
 * a lone YouTube link becomes a taped-in video, task headings get a margin tag,
 * external links open in a new tab, fill-in templates get a copy button.
 */
function md(text) {
  const src = text.replace(/==([^=\n]+)==/g, '<mark>$1</mark>');
  let html = marked.parse(src);
  html = html.replace(/<p><img src="([^"]+)" alt="([^"]*)"(?: title="[^"]*")?>\s*<\/p>/g,
    // the caption describes the figure, so the image itself gets an empty alt (no double reading)
    (_, s, a) => `<figure class="taped"><img src="${s}" alt="" loading="lazy">${a ? `<figcaption>${a}</figcaption>` : ''}</figure>`);
  html = html.replace(/<p><a href="(https?:\/\/(?:www\.)?(?:youtube\.com|youtu\.be)[^"]+)">([^<]*)<\/a><\/p>/g,
    (m, u, t) => { const id = youtubeId(u); return id ? videoBlock(id, t.startsWith('http') ? 'Video' : t) : m; });
  html = html.replace(/<h3>(Must|Stretch|Optional|Bonus): ?([\s\S]*?)<\/h3>/g,
    (_, k, t) => `<h3 class="task ${k.toLowerCase()}" data-tag="${k === 'Must' ? 'must do' : k.toLowerCase()}"><span class="sr-only">${k === 'Must' ? 'Must do' : k}: </span>${t}</h3>`);
  html = html.replace(/<h2>Have ready for class<\/h2>/, '<h2 id="have-ready">Have ready for class</h2>');
  // a resource named without a link gets a pencil note, so nothing looks clickable that is not
  html = html.replace(/(<h2>Resources<\/h2>\s*<ul>)([\s\S]*?)(<\/ul>)/, (_, a, list, z) => a + list.replace(/<li>(?![\s\S]*?<a )([\s\S]*?)<\/li>/g, '<li>$1 <span class="later">link coming before class</span></li>') + z);
  html = html.replace(/<a href="(https?:\/\/[^"]+)"/g, '<a href="$1" target="_blank" rel="noopener"');
  html = html.replace(/<pre><code>/g, '<div class="card-in"><button class="copy" type="button">copy</button><pre><code>').replace(/<\/code><\/pre>/g, '</code></pre></div>');
  return html;
}

/* ---------- layout ---------- */
const FONTS = 'https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400..700;1,7..72,400..600&family=Shantell+Sans:wght@400;500;600&family=Instrument+Serif&family=Geist+Mono:wght@400;500&display=swap';
let previewMe = null;

function layout({ title, body, active = '', bodyClass = '' }) {
  const nav = [['/', 'Home', 'home'], ['/weeks/', 'Weeks', 'weeks'], ['/resources/', 'Resources', 'resources'], ['/me', 'My page', 'me']]
    .map(([h, l, k]) => `<a href="${h}"${active === k ? ' aria-current="page"' : ''}>${l}</a>`).join('');
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · Sterling Robotics Academy</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="${FONTS}">
<link rel="stylesheet" href="/assets/site.css">
<script>if(!matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('motion')</script>
</head>
<body class="${bodyClass}">
<a class="skip" href="#main">Skip to the page</a>
<header class="head"><div class="head-in">
  <a class="brand" href="/"><b>Sterling</b><span>Robotics Academy</span></a>
  <nav aria-label="Main">${nav}</nav>
</div></header>
<main class="sheet" id="main">${body}</main>
<footer class="foot"><p>Stuck or have a question? WhatsApp Swarit on <a href="${esc(site.whatsappLink)}" target="_blank" rel="noopener">${esc(site.whatsapp)}</a>, or email <a href="mailto:${esc(site.email)}">${esc(site.email)}</a>.</p></footer>
${PREVIEW ? `<script>window.__ME=${JSON.stringify(previewMe)}</script>` : ''}
<script src="/assets/app.js" defer></script>
</body></html>`;
}

/* ---------- weeks ---------- */
const weekDirs = fs.readdirSync(C('weeks')).filter(d => /^week-\d{2}$/.test(d)).sort();
const weeks = weekDirs.map(d => {
  const n = Number(d.slice(5));
  const { meta, body } = read(C(`weeks/${d}/index.md`));
  const q = body.match(/^>\s*(.+)$/m);
  return { n, dir: d, meta, body, url: `/weeks/${d}/`, question: q ? q[1].trim() : '' };
});

/* Sample data for the design preview only: a founding-cohort student in week 2. */
if (PREVIEW) {
  const DAY = 86400000, first = new Date(`${schedule.cohorts.founding.firstClass}T12:00:00Z`);
  const ymd = d => d.toISOString().slice(0, 10);
  previewMe = {
    name: 'Sample Student', admin: false, slug: 'sample-student', cohort: 'founding', cohortLabel: schedule.cohorts.founding.label,
    site: { classDay: site.classDay, classTime: site.classTime, meetLink: '', homeworkForm: '', oneOnOneLink: '', whatsapp: site.whatsapp, whatsappLink: site.whatsappLink },
    weeks: weeks.map(w => { const c = new Date(first.getTime() + (w.n - 1) * 7 * DAY); return { n: w.n, title: w.meta.title, short: w.meta.short || w.meta.title, kit: w.meta.kit || '', question: w.question, url: w.url, classDate: ymd(c), unlockDate: ymd(new Date(c.getTime() - 6 * DAY)), unlocked: w.n <= 2 }; }),
    next: 2,
  };
}

for (const [i, w] of weeks.entries()) {
  const dir = C(`weeks/${w.dir}`);
  const files = fs.readdirSync(dir, { withFileTypes: true }).filter(e => e.isFile() && e.name !== 'index.md' && !e.name.startsWith('.'));
  copyDir(dir, path.join(OUT, 'weeks', w.dir), e => e.name === 'index.md' || e.name.startsWith('.'));
  const solDir = path.join(dir, 'solutions');
  const solFiles = fs.existsSync(solDir) ? fs.readdirSync(solDir).filter(f => !f.startsWith('.')) : [];

  const yt = youtubeId(w.meta.recording);
  const recording = `<section><h2>Class recording</h2>${yt ? videoBlock(yt, `Week ${w.n} class recording`)
    : `<div class="pending"><p>The recording goes here after Sunday's class.</p></div>`}</section>`;
  const fileList = [
    ...(w.meta.slides ? [`<li><a href="${esc(w.meta.slides)}" target="_blank" rel="noopener">Class slides</a><span>link</span></li>`] : []),
    ...files.map(f => `<li><a href="${w.url}${encodeURIComponent(f.name)}" download>${esc(f.name)}</a><span>${size(fs.statSync(path.join(dir, f.name)).size)}</span></li>`),
  ];
  const filesBlock = fileList.length ? `<section><h2>Files</h2><ul class="leaders">${fileList.join('')}</ul></section>` : '';
  const solBlock = solFiles.length ? `<section><h2>Solutions</h2><p class="aside-note">These open the Saturday after class.</p><ul class="leaders">${solFiles.map(f => `<li><a href="${w.url}solutions/${encodeURIComponent(f)}">${esc(f)}</a><span>after class</span></li>`).join('')}</ul></section>` : '';

  let html = md(w.body);
  let question = '';
  html = html.replace(/^<blockquote>\s*<p>([\s\S]*?)<\/p>\s*<\/blockquote>/, (_, q) => { question = q; return ''; });
  // "Have ready for class" is what the highlighted line points to, so it comes first
  const ready = html.match(/<h2 id="have-ready">[\s\S]*?(?=<h2|$)/);
  if (ready) { const first = html.search(/<h2/); html = html.replace(ready[0], ''); html = html.slice(0, first) + ready[0] + html.slice(first); }
  const prev = weeks[i - 1], next = weeks[i + 1];
  const body = `
  <aside class="margin">
    <p class="wk" aria-label="Week ${w.n} of ${weeks.length}">week <b>${w.n}</b> <span>of ${weeks.length}</span></p>
    <p class="note" data-week-date="${w.n}"></p>
    <p class="note">${esc(w.meta.kit || '')}</p>
  </aside>
  <article class="col prose">
    <h1>${esc(w.meta.title)}</h1>
    ${question ? `<p class="question">${question}</p>` : ''}
    <p class="todo"><mark class="sweep" data-todo-week="${w.n}">Before Sunday, get the things below ready. After class, do the tasks and submit them.</mark></p>
    ${html}
    ${recording}
    ${filesBlock}${solBlock}
    <section class="submit" id="submit"><h2>Submit your work</h2><p>Send everything for this week in one go: links, photos and your filled-in tables.</p>
      <p><a class="btn" data-submit="${w.n}" href="#" target="_blank" rel="noopener">Submit week ${w.n} <span class="arr" aria-hidden="true">→</span></a></p></section>
    <nav class="pager" aria-label="Weeks">${prev ? `<a href="${prev.url}" rel="prev"><span>previous</span>Week ${prev.n}: ${esc(prev.meta.title)}</a>` : '<span></span>'}${next ? `<a href="${next.url}" rel="next"><span>next</span>Week ${next.n}: ${esc(next.meta.title)}</a>` : '<span></span>'}</nav>
  </article>`;
  write(`weeks/${w.dir}/index.html`, layout({ title: `Week ${w.n}: ${w.meta.title}`, body, active: 'weeks', bodyClass: 'week' }));
}

write('data/weeks.json', JSON.stringify(weeks.map(w => ({ n: w.n, title: w.meta.title, short: w.meta.short || w.meta.title, kit: w.meta.kit || '', question: w.question, url: w.url }))));

const contents = weeks.map(w => `<li data-week="${w.n}"><a href="${w.url}"><span class="n">${w.n}</span><span class="t">${esc(w.meta.title)}</span><span class="d" data-week-when="${w.n}">${esc(w.meta.kit || '')}</span></a></li>`).join('');

write('weeks/index.html', layout({
  title: 'Weeks', active: 'weeks',
  body: `<aside class="margin"><p class="note">12 Sundays.<br>A week opens the Monday before its class.</p></aside>
  <div class="col"><h1>Weeks</h1><ol class="contents">${contents}</ol></div>`,
}));

/* ---------- home (filled in by app.js) ---------- */
write('index.html', layout({
  title: 'Home', active: 'home', bodyClass: 'home',
  body: `<aside class="margin" id="homeMargin"><p class="note">&nbsp;</p></aside>
  <div class="col">
    <h1 id="hello">Welcome back</h1>
    <p class="lede" id="nowLine">&nbsp;</p>
    <p class="todo"><mark class="sweep" id="todo">Loading this week…</mark></p>
    <p class="actions" id="actions"></p>
    <div id="cohortPick"></div>
    <h2>Contents</h2>
    <ol class="contents" id="homeWeeks">${contents}</ol>
    <h2>Also in this notebook</h2>
    <ul class="leaders more">
      <li><a href="/me">My page</a><span>your 1:1 notes and extra tasks</span></li>
      <li><a href="/resources/">Resources</a><span>setup guides and free tools</span></li>
      <li><a href="#" id="oneOnOne" target="_blank" rel="noopener">Book a 1:1</a><span>30 minutes each week</span></li>
    </ul>
  </div>`,
}));

/* ---------- resources ---------- */
function buildPages(srcDir, urlBase, active) {
  for (const e of fs.readdirSync(srcDir, { withFileTypes: true })) {
    const p = path.join(srcDir, e.name);
    if (e.isDirectory()) { buildPages(p, `${urlBase}${e.name}/`, active); continue; }
    if (e.name === 'index.md') {
      const { meta, body } = read(p);
      const isIndex = urlBase === '/resources/';
      write(`${urlBase.slice(1)}index.html`, layout({
        title: meta.title, active,
        body: `<aside class="margin">${isIndex ? '<p class="note">Keep these handy all course.</p>' : '<p class="note"><a href="/resources/">back to resources</a></p>'}</aside>
        <article class="col prose"><h1>${esc(meta.title)}</h1>${md(body)}</article>`,
      }));
    } else if (!e.name.endsWith('.md')) {
      fs.mkdirSync(path.join(OUT, urlBase), { recursive: true }); fs.copyFileSync(p, path.join(OUT, urlBase, e.name));
    }
  }
}
buildPages(C('resources'), '/resources/', 'resources');

/* ---------- student pages (private, checked by lib/guard.js) ---------- */
for (const s of students) {
  const f = C(`students/${s.slug}.md`);
  const { body } = fs.existsSync(f) ? read(f) : { body: '_Notes from your 1:1 sessions will appear here._' };
  write(`students/${s.slug}/index.html`, layout({
    title: s.name, active: 'me', bodyClass: 'mine',
    body: `<aside class="margin"><p class="note">Grade ${esc(s.grade || '')}<br>Only you and Swarit can see this page.</p></aside>
    <article class="col prose"><h1>${esc(s.name)}</h1>${md(body)}</article>`,
  }));
}
write('students/index.html', layout({
  title: 'Students', active: 'me',
  body: `<aside class="margin"><p class="note">Only you can see this list.</p></aside>
  <div class="col"><h1>Students</h1><ul class="leaders">${students.map(s => `<li><a href="/students/${s.slug}/">${esc(s.name)}</a><span>grade ${esc(s.grade || '')}, ${esc(s.cohort)}</span></li>`).join('')}</ul></div>`,
}));

/* ---------- 404 + assets ---------- */
write('404.html', layout({ title: 'Not found', body: '<aside class="margin"></aside><div class="col"><h1>This page is not in the notebook</h1><p><a href="/">Back to home</a></p></div>' }));
copyDir(path.join(ROOT, 'assets'), path.join(OUT, 'assets'));
fs.copyFileSync(path.join(ROOT, 'assets', 'favicon.svg'), path.join(OUT, 'favicon.svg'));
write('robots.txt', 'User-agent: *\nDisallow: /\n');

console.log(`Built ${weeks.length} weeks, ${students.length} student pages into ${path.basename(OUT)}/`);
