// Student platform: Volts, quick quizzes, hints, task submissions, progress and Swarit's review page.
// Prototype: Volts, submissions and reviews are saved in this browser (localStorage) so the feel can be
// tried before the database exists. Quiz answers and hints come from the Worker (/api/quiz, /api/hint),
// never from the page. The real version saves everything in D1 (see the PRD in the vault).
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const longDay = d => new Date(`${d}T12:00:00Z`).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', timeZone: 'UTC' });
  const addDays = (d, n) => new Date(new Date(`${d}T12:00:00Z`).getTime() + n * 86400000).toISOString().slice(0, 10);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  let me = null, plat = null, R = null;
  const KEY = 'sra.platform.v1';

  /* ---------- storage (prototype: this browser only) ---------- */
  function loadAll() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (_) { return {}; } }
  function saveAll(all) { try { localStorage.setItem(KEY, JSON.stringify(all)); } catch (_) {} }
  function blank() { return { ledger: [], res: {}, tries: {}, hints: {}, subs: {}, seen: null }; }
  function state(slug = me.slug) { const all = loadAll(); return all[slug] || blank(); }
  function save(st, slug = me.slug) { const all = loadAll(); all[slug] = st; saveAll(all); }
  const balance = st => st.ledger.reduce((s, r) => s + r.amt, 0);
  function earn(st, amt, reason, ref) {
    if (st.ledger.some(r => r.reason === reason && r.ref === ref)) return 0; // each thing pays once
    st.ledger.push({ amt, reason, ref, at: me.today });
    return amt;
  }

  /* ---------- small UI pieces ---------- */
  function battery(v) {
    const w = Math.round(Math.max(0, Math.min(1, v / 100)) * 19);
    return `<svg class="batt" viewBox="0 0 28 14" aria-hidden="true"><rect x=".75" y=".75" width="23.5" height="12.5" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="25" y="4.5" width="2.25" height="5" rx="1" fill="currentColor"/><rect class="lvl" x="2.75" y="2.75" width="${w}" height="8.5" rx="1"/></svg>`;
  }
  function meter() {
    if (!me || me.admin) return;
    let m = $('.volts');
    const v = balance(state());
    if (!m) {
      m = document.createElement('a');
      m.className = 'volts';
      m.href = '/me';
      $('.head-in').appendChild(m);
    }
    m.innerHTML = `${battery(v)}<b>${v}</b><span>Volts</span>`;
    m.setAttribute('aria-label', `${v} Volts. Open my progress`);
  }
  function flash(text) {
    meter();
    const m = $('.volts'); if (!m) return;
    if (!reduced) { m.classList.remove('gain'); void m.offsetWidth; m.classList.add('gain'); }
    const live = $('#voltsLive') || Object.assign(document.createElement('p'), { id: 'voltsLive', className: 'sr-only' });
    live.setAttribute('aria-live', 'polite'); document.body.appendChild(live); live.textContent = text;
  }
  async function post(path, body) {
    const r = await fetch(path, { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
    if (!r.ok) throw r.status;
    return r.json();
  }
  const weekOf = id => Number((id.match(/^w(\d{2})-/) || [])[1]);
  const weekInfo = n => me.weeks.find(w => w.n === n) || {};
  const outline = n => (plat.weeks || []).find(w => w.n === n);
  const dueDate = n => { const w = weekInfo(n); return w.classDate ? addDays(w.classDate, 6) : null; };
  const lastSub = (st, id) => { const s = st.subs[id]; return s && s.length ? s[s.length - 1] : null; };

  /* ---------- next step for a week ---------- */
  function nextStep(n, st) {
    const o = outline(n); if (!o) return null;
    const r = o.resources.find(x => !st.res[x.id]);
    if (r) return { verb: 'Read', title: r.title, url: r.url };
    const t = o.tasks.find(x => x.kind === 'must' && !lastSub(st, x.id)) || o.tasks.find(x => !lastSub(st, x.id));
    if (t) return { verb: 'Do', title: t.title, url: t.url };
    const redo = o.tasks.find(x => (lastSub(st, x.id) || {}).status === 'redo');
    if (redo) return { verb: 'Redo', title: redo.title, url: redo.url };
    return null;
  }

  /* ---------- pages ---------- */
  function home() {
    if (!document.body.classList.contains('home') || me.admin) return;
    const st = state();
    if (!st.seen) {
      st.seen = me.today;
      earn(st, R.welcome, 'welcome', 'welcome');
      save(st);
      const card = document.createElement('div');
      card.className = 'welcome taped-note';
      card.innerHTML = `<p class="hand">How this notebook works</p>
        <ol><li><b>Read</b> the short pages each week. Pass the quick quiz to earn Volts.</li>
        <li><b>Stuck?</b> Spend Volts on a hint.</li>
        <li><b>Submit</b> each task on its own page. Swarit reviews it.</li></ol>
        <p class="gift">Here are <b>${R.welcome} Volts</b> to start. Try a hint when you need one.</p>`;
      $('#hello').after(card);
      flash(`You got ${R.welcome} Volts to start.`);
    }
    const cur = me.weeks.find(w => w.n === me.next && w.unlocked) || me.weeks.filter(w => w.unlocked).pop();
    if (!cur || !outline(cur.n)) return;
    const step = nextStep(cur.n, st);
    const todo = $('#todo'), actions = $('#actions');
    if (step) {
      todo.textContent = `Next: ${step.verb.toLowerCase()} “${step.title}”.`;
      actions.innerHTML = `<a class="btn" href="${esc(step.url)}">${esc(step.verb)}: ${esc(step.title)} <span class="arr" aria-hidden="true">→</span></a><a class="quiet" href="${esc(cur.url)}">All of week ${cur.n}</a>`;
    } else {
      todo.textContent = `Week ${cur.n} is all submitted. Swarit will review it.`;
    }
    todo.classList.remove('sweep'); void todo.offsetWidth; todo.classList.add('sweep');
  }

  function weekPage() {
    const art = $('article[data-week]'); if (!art || !$('.steps')) return;
    const n = Number(art.dataset.week), st = state(), o = outline(n);
    if (!o) return;
    o.resources.forEach(r => {
      const el = $(`[data-state="${r.id}"]`), li = el && el.closest('li');
      if (st.res[r.id]) { li.classList.add('done'); el.innerHTML = `<span class="tick" aria-hidden="true">✓</span> done`; }
    });
    o.tasks.forEach(t => {
      const el = $(`[data-state="${t.id}"]`), li = el && el.closest('li'), s = lastSub(st, t.id);
      if (!s) return;
      const label = { submitted: 'submitted', done: 'done', redo: 'redo' }[s.status];
      li.classList.add(s.status === 'done' ? 'done' : s.status === 'redo' ? 'redo' : 'sent');
      el.innerHTML = s.status === 'done' ? `<span class="tick" aria-hidden="true">✓</span> done` : esc(label);
    });
    const mark = $(`[data-next-step="${n}"]`), step = me.admin ? null : nextStep(n, st);
    if (mark) mark.innerHTML = step ? `Next: ${esc(step.verb.toLowerCase())} <a href="${esc(step.url)}">“${esc(step.title)}”</a>.`
      : me.admin ? 'Students see their next step here.' : 'All submitted. Swarit will review your work.';
    const nextLi = step && $$('.steps li').find(li => (li.querySelector('a') || {}).getAttribute && li.querySelector('a').getAttribute('href') === step.url);
    if (nextLi) nextLi.classList.add('now');
  }

  function resourcePage() {
    const form = $('form[data-quiz]'); if (!form) return;
    const id = form.dataset.quiz, st = state();
    const result = $('.quiz-result', form);
    const doneMsg = got => { form.classList.add('passed'); $$('input', form).forEach(i => (i.disabled = true)); $('button', form).hidden = true;
      result.innerHTML = `<mark>Passed.</mark> ${got ? `+${got} Volts.` : 'You already earned Volts for this page.'} ${nextHint()}`; };
    const nextHint = () => { const a = $('.pager a[rel="next"]'); return a ? `<a href="${esc(a.getAttribute('href'))}">Next: ${esc(a.lastChild.textContent)} →</a>` : ''; };
    if (st.res[id]) { doneMsg(0); return; }
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const answers = {};
      let missing = 0;
      $$('fieldset.q', form).forEach(f => { const c = $('input:checked', f); if (c) answers[f.dataset.q] = c.value; else missing++; });
      if (missing) { result.textContent = `Answer all ${$$('fieldset.q', form).length} questions first.`; return; }
      $('button', form).disabled = true;
      try {
        const r = await post('/api/quiz', { resource: id, answers });
        $$('.why', form).forEach(p => { p.hidden = true; p.textContent = ''; });
        $$('fieldset.q', form).forEach(f => f.classList.remove('wrong'));
        const s = state();
        s.tries[id] = (s.tries[id] || 0) + 1;
        if (r.pass) {
          s.res[id] = { at: me.today, first: s.tries[id] === 1 };
          const got = me.admin ? 0 : earn(s, s.tries[id] === 1 ? R.quizFirst : R.quizRetry, 'quiz', id);
          save(s); doneMsg(got); if (got) flash(`Passed. You earned ${got} Volts.`);
        } else {
          save(s);
          r.wrong.forEach(w => { const f = $(`fieldset[data-q="${w.q}"]`, form); f.classList.add('wrong'); const p = $('.why', f); p.textContent = w.why || 'Look again at the page above.'; p.hidden = false; });
          result.textContent = `${r.wrong.length === 1 ? 'One answer needs' : `${r.wrong.length} answers need`} another look. Read the note under it, then try again. A second try earns ${R.quizRetry} Volts.`;
        }
      } catch (_) { result.textContent = 'Could not check your answers. Reload the page and try again.'; }
      $('button', form).disabled = false;
    });
  }

  function taskPage() {
    const art = $('article[data-task-page]'); if (!art) return;
    const id = art.dataset.taskPage, n = Number(art.dataset.week), w = weekInfo(n);
    const free = !!w.solutionsOpen;
    const freeNote = $(`[data-free-from="${n}"]`);
    if (freeNote) freeNote.textContent = free ? 'Hints are free now.' : w.solutionsDate ? `All hints are free from ${longDay(w.solutionsDate)}.` : '';

    // Hints
    $$('[data-hint]').forEach(li => {
      const hid = li.dataset.hint, cost = free || me.admin ? 0 : Number(li.dataset.cost);
      const btn = $('.hintbtn', li), box = $('.hinttext', li);
      const show = text => { box.textContent = text; box.hidden = false; btn.classList.add('open'); $('.cost', btn).textContent = 'opened'; btn.setAttribute('aria-expanded', 'true'); };
      const st0 = state();
      if (st0.hints[hid]) { btn.disabled = true; post('/api/hint', { hint: hid }).then(r => show(r.text)).catch(() => {}); }
      if (cost === 0 && !st0.hints[hid]) $('.cost', btn).textContent = 'free';
      let armed = false;
      btn.addEventListener('click', async () => {
        const st = state();
        if (st.hints[hid]) return;
        if (cost > balance(st)) { box.hidden = false; box.className = 'hinttext short'; box.textContent = `You need ${cost - balance(st)} more Volts. Pass a quiz or submit a task to earn them.`; return; }
        if (cost && !armed) { armed = true; $('.cost', btn).textContent = `spend ${cost}? tap again`; setTimeout(() => { armed = false; if (!state().hints[hid]) $('.cost', btn).textContent = `${cost} Volts`; }, 4000); return; }
        btn.disabled = true;
        try {
          const r = await post('/api/hint', { hint: hid });
          const s = state();
          s.hints[hid] = { at: me.today, cost };
          if (cost) s.ledger.push({ amt: -cost, reason: 'hint', ref: hid, at: me.today });
          save(s); box.className = 'hinttext'; show(r.text);
          if (cost) flash(`Hint opened. ${cost} Volts spent.`);
        } catch (_) { btn.disabled = false; box.hidden = false; box.textContent = 'Could not open the hint. Reload and try again.'; }
      });
    });

    // Submission
    const form = $('form[data-submit-task]'), status = $('.submit-status', form), fb = $('.feedback');
    const render = () => {
      const s = lastSub(state(), id);
      if (!s) return;
      fb.hidden = false;
      if (s.status === 'done') { fb.className = 'feedback ok'; fb.innerHTML = `<p class="hand">Done ✓</p>${s.comment ? `<p>${esc(s.comment)}</p>` : ''}<p class="aside-note">Reviewed by Swarit.</p>`; form.hidden = true; }
      else if (s.status === 'redo') { fb.className = 'feedback redo'; fb.innerHTML = `<p class="hand">Redo</p><p>${esc(s.comment || 'Have another go.')}</p><p class="aside-note">Fix it and submit again below.</p>`; form.hidden = false; }
      else { fb.className = 'feedback sent'; fb.innerHTML = `<p class="hand">Submitted ${esc(longDay(s.at))}</p><p class="aside-note">Swarit reviews work within 48 hours. You can change it until then.</p>`; }
    };
    render();
    if (me.admin) { form.querySelector('button').disabled = true; status.textContent = 'Students submit here. Review their work on the Review page.'; return; }
    form.addEventListener('submit', e => {
      e.preventDefault();
      const body = (form.body && form.body.value || '').trim();
      const linkEl = form.link, link = (linkEl && linkEl.value || '').trim();
      const kind = form.dataset.kind;
      if ((kind === 'text' || kind === 'both') && !body) { status.textContent = 'Paste your work in the box first.'; form.body.focus(); return; }
      if ((kind === 'link' || kind === 'both') && !/^https?:\/\/\S+\.\S+/.test(link)) { status.textContent = 'Add a full link that starts with https://'; linkEl.focus(); return; }
      const st = state();
      st.subs[id] = st.subs[id] || [];
      st.subs[id].push({ v: st.subs[id].length + 1, body, link, at: me.today, status: 'submitted' });
      let got = earn(st, R.taskSubmitted, 'submit', id);
      const due = dueDate(n);
      if (due && me.today <= due) got += earn(st, R.onTime, 'ontime', id);
      save(st); render();
      const next = $('.pager a[rel="next"]');
      status.innerHTML = `Saved.${got ? ` +${got} Volts.` : ''} ${next ? `<a href="${esc(next.getAttribute('href'))}">${esc(next.lastChild.textContent)} →</a>` : ''}`;
      if (got) flash(`Submitted. You earned ${got} Volts.`);
    });
  }

  function myPage() {
    const art = $('.mine article'); if (!art || me.admin) return;
    const st = state(), v = balance(st);
    const rows = (plat.weeks || []).map(o => {
      const w = weekInfo(o.n), rd = o.resources.filter(r => st.res[r.id]).length;
      const td = o.tasks.filter(t => (lastSub(st, t.id) || {}).status === 'done').length, ts = o.tasks.filter(t => lastSub(st, t.id)).length;
      return w.unlocked ? `<li><a href="${esc(w.url)}"><span class="n">${o.n}</span><span class="t">${esc(w.title)}</span><span class="d">read ${rd}/${o.resources.length} · sent ${ts}/${o.tasks.length} · done ${td}</span></a></li>` : '';
    }).join('');
    const hist = st.ledger.slice(-8).reverse().map(r => `<li><span>${esc({ welcome: 'Welcome gift', quiz: 'Quiz passed', submit: 'Task submitted', ontime: 'On time', done: 'Task done', hint: 'Hint opened', gift: 'Gift from Swarit' }[r.reason] || r.reason)}</span><span class="${r.amt < 0 ? 'neg' : ''}">${r.amt > 0 ? '+' : ''}${r.amt}</span></li>`).join('');
    const sec = document.createElement('section');
    sec.className = 'progress';
    sec.id = 'volts';
    sec.innerHTML = `<h2>Your progress</h2>
      <p class="bal">${battery(v)}<b>${v}</b> Volts</p>
      ${rows ? `<ol class="contents">${rows}</ol>` : '<p class="aside-note">Progress shows here once week 1 opens.</p>'}
      ${hist ? `<h3>Recent Volts</h3><ul class="ledger">${hist}</ul>` : ''}`;
    $('h1', art).after(sec);
  }

  function adminPage() {
    if (!document.body.classList.contains('adminpage')) return;
    const all = loadAll(), items = [];
    Object.entries(all).forEach(([slug, st]) => Object.entries(st.subs || {}).forEach(([tid, list]) => {
      const s = list[list.length - 1];
      if (s.status === 'submitted') items.push({ slug, tid, s });
    }));
    const title = tid => { const o = outline(weekOf(tid)); const t = o && o.tasks.find(x => x.id === tid); return t ? t : { title: tid, kind: 'must', url: '#' }; };
    const q = $('#reviewQueue');
    q.innerHTML = items.length ? items.map((it, i) => {
      const t = title(it.tid);
      return `<article class="review" data-i="${i}"><p class="crumb">${esc(it.slug.replace(/-/g, ' '))} · week ${weekOf(it.tid)} · submitted ${esc(longDay(it.s.at))}</p>
        <h3><a href="${esc(t.url)}">${esc(t.title)}</a> <span class="tag k-${esc(t.kind)}">${esc(t.kind === 'must' ? 'must do' : t.kind)}</span></h3>
        ${it.s.body ? `<pre class="work"></pre>` : ''}${it.s.link ? `<p><a class="worklink" target="_blank" rel="noopener noreferrer"></a></p>` : ''}
        <label class="field"><span>Comment (optional)</span><textarea rows="2"></textarea></label>
        <p class="quiz-actions"><button class="btn" data-v="done">Done</button> <button class="quiet" data-v="redo">Redo</button></p></article>`;
    }).join('') : '<p class="aside-note">Nothing waiting. Submissions from students appear here.</p>';
    $$('.review', q).forEach(el => {
      const it = items[Number(el.dataset.i)];
      const pre = $('.work', el); if (pre) pre.textContent = it.s.body;
      const a = $('.worklink', el); if (a) { a.textContent = it.s.link; if (/^https?:\/\//.test(it.s.link)) a.href = it.s.link; }
      $$('button[data-v]', el).forEach(b => b.addEventListener('click', () => {
        const store = loadAll(), st = store[it.slug], s = st.subs[it.tid][st.subs[it.tid].length - 1];
        s.status = b.dataset.v; s.comment = $('textarea', el).value.trim();
        if (s.status === 'done') { const t = title(it.tid); const amt = t.kind === 'stretch' || t.kind === 'bonus' ? R.stretchDone : R.taskDone; if (!st.ledger.some(r => r.reason === 'done' && r.ref === it.tid)) st.ledger.push({ amt, reason: 'done', ref: it.tid, at: me.today }); }
        saveAll(store);
        el.innerHTML = `<p class="aside-note">Marked ${esc(s.status)}. The student sees it on the task page.</p>`;
      }));
    });
    $('#roster').innerHTML = `<ul class="leaders">${Object.entries(all).map(([slug, st]) => {
      const sent = Object.keys(st.subs || {}).length, read = Object.keys(st.res || {}).length;
      return `<li><span>${esc(slug.replace(/-/g, ' '))}</span><span>${balance(st)} Volts · ${read} pages read · ${sent} tasks sent</span></li>`;
    }).join('') || '<li><span>No activity yet</span><span></span></li>'}</ul>`;
  }

  function adminNav() {
    if (!me.admin) return;
    const nav = $('.head nav'); if (!nav || $('a[href="/admin/"]', nav)) return;
    const a = document.createElement('a'); a.href = '/admin/'; a.textContent = 'Review';
    if (document.body.classList.contains('adminpage')) a.setAttribute('aria-current', 'page');
    nav.appendChild(a);
  }

  /* ---------- preview controls (preview Workers only) ---------- */
  function previewBar() {
    if (!me.preview) return;
    const dates = [
      ['', 'Real today'], ['2026-11-09', 'Mon 9 Nov: week 1 opens'], ['2026-11-15', 'Sun 15 Nov: class 1'],
      ['2026-11-16', 'Mon 16 Nov: week 2 opens'], ['2026-11-21', 'Sat 21 Nov: week 1 hints free'], ['2026-11-23', 'Mon 23 Nov: week 3 opens'],
      ['2026-12-14', 'Mon 14 Dec: week 6 opens'], ['2027-01-25', 'Mon 25 Jan: week 12 opens'],
    ];
    const cur = (document.cookie.match(/(?:^|; )sim_date=([^;]+)/) || [])[1] || '';
    const bar = document.createElement('div');
    bar.className = 'previewbar';
    bar.innerHTML = `<p><b>Preview</b> Pretend today is
      <select aria-label="Pretend today is">${dates.map(([v, l]) => `<option value="${v}"${v === cur ? ' selected' : ''}>${l}</option>`).join('')}</select>
      · view as <button type="button" data-as="student"${me.admin ? '' : ' aria-pressed="true"'}>Student</button><button type="button" data-as="admin"${me.admin ? ' aria-pressed="true"' : ''}>Swarit</button>
      · <button type="button" data-reset>Reset progress</button></p>
      <p class="small">Nothing is pushed between these dates. The site opens each week by itself on its Monday.</p>`;
    document.body.appendChild(bar);
    const set = (k, v) => { document.cookie = `${k}=${v}; path=/; max-age=${v ? 86400 : 0}; samesite=lax`; location.reload(); };
    $('select', bar).onchange = e => set('sim_date', e.target.value);
    $$('[data-as]', bar).forEach(b => (b.onclick = () => set('sim_as', b.dataset.as)));
    $('[data-reset]', bar).onclick = () => { try { localStorage.removeItem(KEY); } catch (_) {} location.reload(); };
  }

  function start(m) {
    me = m;
    fetch('/data/platform.json', { credentials: 'same-origin' }).then(r => r.json()).then(p => {
      plat = p; R = p.rewards;
      adminNav(); meter(); home(); weekPage(); resourcePage(); taskPage(); myPage(); adminPage(); previewBar();
    }).catch(() => {});
  }
  if (window.__me) start(window.__me);
  else document.addEventListener('sra:me', e => setTimeout(() => start(e.detail), 0), { once: true });
})();
