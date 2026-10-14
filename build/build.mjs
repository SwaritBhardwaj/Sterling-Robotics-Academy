// Builds the course site from content/ into dist/.
// Run: npm run build. Cloudflare runs this on every push to main.
import fs from 'node:fs';
import path from 'node:path';
import { marked } from 'marked';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const C = p => path.join(ROOT, 'content', p);
const OUT = path.join(ROOT, 'dist');
const site = JSON.parse(fs.readFileSync(C('site.json'), 'utf8'));
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
function write(rel, html) { const f = path.join(OUT, rel); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, html); }
function copyDir(src, dst, skip = () => false) {
  if (!fs.existsSync(src)) return;
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name), d = path.join(dst, e.name);
    if (skip(e, s)) continue;
    if (e.isDirectory()) copyDir(s, d, skip);
    else { fs.mkdirSync(dst, { recursive: true }); fs.copyFileSync(s, d); }
  }
}
const pad = n => String(n).padStart(2, '0');
const size = b => b > 1048576 ? `${(b / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1024))} KB`;

/** Markdown to HTML, plus course touches: task chips, links in new tabs, copy buttons on templates. */
function md(text) {
  let html = marked.parse(text);
  html = html.replace(/<h3>(Must|Stretch|Optional|Bonus): ?([\s\S]*?)<\/h3>/g, (_, k, t) => `<h3 class="task"><span class="chip ${k.toLowerCase()}">${k}</span>${t}</h3>`);
  html = html.replace(/<a href="(https?:\/\/[^"]+)"/g, '<a href="$1" target="_blank" rel="noopener"');
  html = html.replace(/<pre><code>/g, '<div class="tpl"><button class="copy" type="button">Copy</button><pre><code>').replace(/<\/code><\/pre>/g, '</code></pre></div>');
  return html;
}
function youtubeId(u) { const m = String(u || '').match(/(?:youtu\.be\/|v=|embed\/|shorts\/)([\w-]{11})/); return m ? m[1] : null; }

/* ---------- layout ---------- */
function layout({ title, body, active = '', bodyClass = '' }) {
  const nav = [['/', 'Home', 'home'], ['/weeks/', 'Weeks', 'weeks'], ['/resources/', 'Resources', 'resources'], ['/me', 'My page', 'me']]
    .map(([h, l, k]) => `<a href="${h}" class="${active === k ? 'on' : ''}">${l}</a>`).join('');
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} · Sterling Robotics Academy</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif&family=Geist+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/site.css"></head>
<body class="${bodyClass}">
<header class="nav"><div class="wrap navin"><a class="brand" href="/"><b>Sterling</b><span>ROBOTICS ACADEMY</span></a><nav>${nav}</nav></div></header>
<main class="wrap">${body}</main>
<footer class="wrap foot"><span>Questions? WhatsApp ${esc(site.whatsapp)} or ${esc(site.email)}</span></footer>
<script src="/assets/app.js" defer></script>
</body></html>`;
}

/* ---------- weeks ---------- */
const weekDirs = fs.readdirSync(C('weeks')).filter(d => /^week-\d{2}$/.test(d)).sort();
const weeks = weekDirs.map(d => {
  const n = Number(d.slice(5));
  const { meta, body } = read(C(`weeks/${d}/index.md`));
  return { n, dir: d, meta, body, url: `/weeks/${d}/` };
});

for (const [i, w] of weeks.entries()) {
  const dir = C(`weeks/${w.dir}`);
  const files = fs.readdirSync(dir, { withFileTypes: true }).filter(e => e.isFile() && e.name !== 'index.md' && !e.name.startsWith('.'));
  const hasSolutions = fs.existsSync(path.join(dir, 'solutions'));
  copyDir(dir, path.join(OUT, 'weeks', w.dir), e => e.name === 'index.md' || e.name.startsWith('.'));
  const solFiles = hasSolutions ? fs.readdirSync(path.join(dir, 'solutions')).filter(f => !f.startsWith('.')) : [];

  const yt = youtubeId(w.meta.recording);
  const recording = yt
    ? `<section class="block"><h2>Class recording</h2><div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${yt}" title="Week ${w.n} recording" allow="accelerometer; encrypted-media; picture-in-picture; fullscreen" allowfullscreen loading="lazy"></iframe></div></section>`
    : `<section class="block"><h2>Class recording</h2><p class="muted">Added here after Sunday's class.</p></section>`;
  const fileList = [
    ...(w.meta.slides ? [`<li><a href="${esc(w.meta.slides)}" target="_blank" rel="noopener">Class slides</a></li>`] : []),
    ...files.map(f => `<li><a href="${w.url}${encodeURIComponent(f.name)}" download>${esc(f.name)}</a><span class="muted">${size(fs.statSync(path.join(dir, f.name)).size)}</span></li>`),
  ];
  const filesBlock = fileList.length ? `<section class="block"><h2>Files</h2><ul class="files">${fileList.join('')}</ul></section>` : '';
  const solBlock = solFiles.length ? `<section class="block"><h2>Solutions</h2><p class="muted">These open the Saturday after class.</p><ul class="files">${solFiles.map(f => `<li><a href="${w.url}solutions/${encodeURIComponent(f)}">${esc(f)}</a></li>`).join('')}</ul></section>` : '';

  let html = md(w.body);
  let question = '';
  html = html.replace(/^<blockquote>\s*<p>([\s\S]*?)<\/p>\s*<\/blockquote>/, (_, q) => { question = q; return ''; });
  const prev = weeks[i - 1], next = weeks[i + 1];
  const body = `
  <div class="weekhead">
    <p class="eyebrow">Week ${pad(w.n)} <span class="dot">·</span> ${esc(w.meta.kit || '')} <span class="dot">·</span> <span data-week-date="${w.n}"></span></p>
    <h1>${esc(w.meta.title)}</h1>
    ${question ? `<p class="question"><span>This week's question</span>${question}</p>` : ''}
  </div>
  ${recording}
  <article class="prose">${html}</article>
  ${filesBlock}${solBlock}
  <section class="block submit"><h2>Submit your work</h2><p>Send everything for this week in one go: links, photos and your filled-in tables.</p>
    <a class="btn" data-submit="${w.n}" href="#" target="_blank" rel="noopener">Submit week ${w.n} ›</a></section>
  <nav class="pager">${prev ? `<a href="${prev.url}">‹ Week ${prev.n}</a>` : '<span></span>'}${next ? `<a href="${next.url}">Week ${next.n} ›</a>` : '<span></span>'}</nav>`;
  write(`weeks/${w.dir}/index.html`, layout({ title: `Week ${w.n}: ${w.meta.title}`, body, active: 'weeks' }));
}

write('data/weeks.json', JSON.stringify(weeks.map(w => ({ n: w.n, title: w.meta.title, short: w.meta.short || w.meta.title, kit: w.meta.kit || '', url: w.url }))));

write('weeks/index.html', layout({
  title: 'Weeks', active: 'weeks',
  body: `<p class="eyebrow">12 Sundays</p><h1>Weeks</h1><p class="lede">Each week opens on the Monday before its class.</p>
  <ol class="weeklist">${weeks.map(w => `<li data-week="${w.n}"><a href="${w.url}"><span class="num">${pad(w.n)}</span><span class="t"><b>${esc(w.meta.title)}</b><small>${esc(w.meta.kit || '')}</small></span><span class="when" data-week-when="${w.n}"></span></a></li>`).join('')}</ol>`,
}));

/* ---------- home (filled in by app.js) ---------- */
write('index.html', layout({
  title: 'Home', active: 'home', bodyClass: 'home',
  body: `<p class="eyebrow" id="cohortLabel">&nbsp;</p><h1 id="hello">Welcome</h1>
  <div id="cohortPick"></div>
  <div class="cards">
    <section class="card blue" id="nextClass"><span class="lab">Next class</span><p class="big">Loading…</p></section>
    <section class="card" id="thisWeek"><span class="lab">This week</span><p class="big">&nbsp;</p></section>
  </div>
  <div class="quick">
    <a href="/me" class="qk"><b>My page</b><span>1:1 notes and your own tasks</span></a>
    <a href="/resources/" class="qk"><b>Resources</b><span>Setup guides and free tools</span></a>
    <a href="#" id="oneOnOne" class="qk"><b>Book a 1:1</b><span>30 minutes each week</span></a>
  </div>
  <h2 class="sec">All weeks</h2><ol class="weeklist" id="homeWeeks"></ol>`,
}));

/* ---------- resources ---------- */
function buildPages(srcDir, urlBase, active) {
  for (const e of fs.readdirSync(srcDir, { withFileTypes: true })) {
    const p = path.join(srcDir, e.name);
    if (e.isDirectory()) { buildPages(p, `${urlBase}${e.name}/`, active); continue; }
    if (e.name === 'index.md') {
      const { meta, body } = read(p);
      write(`${urlBase.slice(1)}index.html`, layout({ title: meta.title, active, body: `<p class="eyebrow">Resources</p><h1>${esc(meta.title)}</h1><article class="prose">${md(body)}</article>` }));
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
    title: s.name, active: 'me',
    body: `<p class="eyebrow">My page <span class="dot">·</span> Grade ${esc(s.grade || '')}</p><h1>${esc(s.name)}</h1><p class="lede">Only you and Swarit can see this page.</p><article class="prose">${md(body)}</article>`,
  }));
}
write('students/index.html', layout({
  title: 'Students', active: 'me',
  body: `<p class="eyebrow">Admin</p><h1>Students</h1><ul class="files">${students.map(s => `<li><a href="/students/${s.slug}/">${esc(s.name)}</a><span class="muted">Grade ${esc(s.grade || '')} · ${esc(s.cohort)}</span></li>`).join('')}</ul>`,
}));

/* ---------- 404 + assets ---------- */
write('404.html', layout({ title: 'Not found', body: '<h1>Page not found</h1><p><a href="/">Back to home</a></p>' }));
copyDir(path.join(ROOT, 'assets'), path.join(OUT, 'assets'));
fs.copyFileSync(path.join(ROOT, 'assets', 'favicon.svg'), path.join(OUT, 'favicon.svg'));
write('robots.txt', 'User-agent: *\nDisallow: /\n');

console.log(`Built ${weeks.length} weeks, ${students.length} student pages into dist/`);
