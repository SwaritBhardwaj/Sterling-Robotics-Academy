// Fills in the parts of each page that depend on who is signed in: dates, locks, this week, links.
(function () {
  const $ = s => document.querySelector(s);
  const $$ = s => document.querySelectorAll(s);
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const day = d => new Date(`${d}T12:00:00Z`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'UTC' });
  const longDay = d => new Date(`${d}T12:00:00Z`).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', timeZone: 'UTC' });

  // Root of the site. "/" when live; a relative path in the design preview.
  const css = document.querySelector('link[href$="assets/site.css"]');
  const ROOT = css ? css.getAttribute('href').replace(/assets\/site\.css$/, '') : '/';
  const PREVIEW = !!window.__ME;
  const link = u => (PREVIEW ? ROOT + u.replace(/^\//, '') + (u.endsWith('/') ? 'index.html' : '') : u);

  // Copy buttons on fill-in templates
  $$('.card-in .copy').forEach(b => b.addEventListener('click', () => {
    const t = b.parentElement.querySelector('code').innerText;
    const done = l => { b.textContent = l; setTimeout(() => (b.textContent = 'copy'), 1600); };
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(() => done('copied'), () => done('select and copy'));
  }));

  // Restart the highlighter sweep after the text inside it changes
  function resweep(el) { el.classList.remove('sweep'); void el.offsetWidth; el.classList.add('sweep'); }

  const cohortParam = new URLSearchParams(location.search).get('cohort');
  const load = PREVIEW ? Promise.resolve(window.__ME)
    : fetch('/api/me' + (cohortParam ? `?cohort=${encodeURIComponent(cohortParam)}` : ''), { credentials: 'same-origin' })
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)));
  load.then(render).catch(() => {
    const t = $('#todo'); if (t) t.textContent = 'Could not load your schedule. Reload the page.';
  });

  function submitUrl(me, n) {
    if (!me.site.homeworkForm) return me.site.whatsappLink || '#';
    const u = new URL(me.site.homeworkForm);
    u.searchParams.set('week', n);
    u.searchParams.set('student', me.name);
    return u.toString();
  }

  function render(me) {
    // platform.js (Volts, quizzes, hints) listens for this
    window.__me = me;
    document.dispatchEvent(new CustomEvent('sra:me', { detail: me }));
    const nw = me.weeks.find(w => w.n === me.next);
    const open = me.weeks.filter(w => w.unlocked);
    const cur = nw && nw.unlocked ? nw : open[open.length - 1];

    // Contents lists (home and weeks index)
    $$('[data-week-when]').forEach(el => {
      const w = me.weeks.find(x => x.n === Number(el.dataset.weekWhen)); if (!w) return;
      const li = el.closest('li');
      const isNow = cur && w.n === cur.n;
      li.className = !w.unlocked ? 'locked' : isNow ? 'now' : '';
      el.textContent = !w.unlocked ? `opens ${day(w.unlockDate)}` : isNow ? 'this week' : `class ${day(w.classDate)}`;
    });

    if (document.body.classList.contains('home')) home(me, nw, cur);

    // Week page
    $$('[data-week-date]').forEach(el => {
      const w = me.weeks.find(x => x.n === Number(el.dataset.weekDate));
      if (w) el.innerHTML = `class on<br><span class="big">${longDay(w.classDate)}</span>`;
    });
    $$('[data-submit]').forEach(a => {
      a.href = submitUrl(me, a.dataset.submit);
      if (!me.site.homeworkForm) a.innerHTML = 'Send your work on WhatsApp <span class="arr" aria-hidden="true">→</span>';
    });
  }

  function home(me, nw, cur) {
    $('#hello').textContent = `Hi ${me.name.split(' ')[0]}`;
    const time = me.site.classTime ? `, ${me.site.classTime}` : '';
    const todo = $('#todo'), now = $('#nowLine'), actions = $('#actions'), margin = $('#homeMargin');

    if (!me.weeks.length) return;
    if (!nw && !cur) {
      now.textContent = '';
      todo.textContent = 'Could not find your class dates. Message Swarit.';
    } else if (!cur) {
      // Course has not started yet
      const w1 = me.weeks[0];
      margin.innerHTML = `<p class="note">${esc(me.cohortLabel)}</p><p class="note">week 1 opens<br><span class="big">${longDay(w1.unlockDate)}</span></p>`;
      now.textContent = 'Your notebook opens the Monday before the first class.';
      todo.textContent = 'Before then, install phyphox on a phone and Arduino IDE 2 on your laptop.';
      actions.innerHTML = `<a class="btn" href="${link('/resources/getting-started/')}">How the course works <span class="arr" aria-hidden="true">→</span></a>`;
    } else if (!nw) {
      margin.innerHTML = `<p class="note">${esc(me.cohortLabel)}</p><p class="note">all 12 weeks done</p>`;
      now.textContent = 'You finished the course. Your notes stay here.';
      todo.textContent = 'Keep the robot balancing, and keep building.';
      actions.innerHTML = `<a class="btn" href="${link('/me')}">My page <span class="arr" aria-hidden="true">→</span></a>`;
    } else {
      margin.innerHTML = `<p class="wk">week <b>${cur.n}</b> <span>of ${me.weeks.length}</span></p>
        <p class="note">next class<br><span class="big">${longDay(nw.classDate)}</span>${esc(time)}</p>
        <p class="note">${esc(me.cohortLabel)}</p>`;
      now.textContent = cur.question || cur.title;
      todo.textContent = `Before Sunday, open week ${cur.n} and get everything under “Have ready for class” done.`;
      actions.innerHTML = `<a class="btn" href="${link(cur.url)}">Open week ${cur.n} <span class="arr" aria-hidden="true">→</span></a>`
        + (me.site.meetLink ? `<a class="quiet" href="${esc(me.site.meetLink)}" target="_blank" rel="noopener">Join Sunday's class</a>` : '');
    }
    resweep(todo);

    if (me.admin && me.cohorts) {
      $('#cohortPick').innerHTML = `<div class="cohortpick">showing ${me.cohorts.map(c => `<button type="button" data-c="${c.key}" class="${c.key === me.cohort ? 'on' : ''}">${esc(c.label)}</button>`).join('')}<a href="${link('/students/')}">all students</a></div>`;
      $$('.cohortpick button').forEach(b => b.onclick = () => { location.search = `?cohort=${b.dataset.c}`; });
    }

    const one = $('#oneOnOne');
    if (one) {
      if (me.site.oneOnOneLink) one.href = me.site.oneOnOneLink;
      else { one.href = me.site.whatsappLink; one.textContent = 'Book a 1:1 on WhatsApp'; }
    }
  }
})();
