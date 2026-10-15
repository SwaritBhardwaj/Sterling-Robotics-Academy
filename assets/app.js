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
  $$('.card-in .copy').forEach(b => b.setAttribute('aria-live', 'polite'));
  $$('.card-in .copy').forEach(b => b.addEventListener('click', () => {
    const t = b.parentElement.querySelector('code').innerText;
    const done = l => { b.textContent = l; setTimeout(() => (b.textContent = 'copy'), 1600); };
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(() => done('copied'), () => done('select and copy'));
  }));

  // Wide templates: fade the right edge and say so, until scrolled to the end
  $$('.card-in').forEach(card => {
    const pre = card.querySelector('pre'); if (!pre) return;
    const check = () => {
      const wide = pre.scrollWidth > pre.clientWidth + 2;
      card.classList.toggle('scrolls', wide);
      card.classList.toggle('at-end', wide && pre.scrollLeft + pre.clientWidth >= pre.scrollWidth - 4);
      let more = card.querySelector('.more');
      if (wide && !more) { more = document.createElement('p'); more.className = 'more'; more.textContent = 'scroll sideways for more →'; card.prepend(more); }
      if (!wide && more) more.remove();
    };
    pre.addEventListener('scroll', check, { passive: true });
    addEventListener('resize', check);
    check();
  });

  // Restart the highlighter sweep after the text inside it changes
  function resweep(el) { el.classList.remove('sweep'); void el.offsetWidth; el.classList.add('sweep'); }

  const cohortParam = new URLSearchParams(location.search).get('cohort');
  const load = PREVIEW ? Promise.resolve(window.__ME)
    : fetch('/api/me' + (cohortParam ? `?cohort=${encodeURIComponent(cohortParam)}` : ''), { credentials: 'same-origin' })
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)));
  load.then(render).catch(() => {
    const t = $('#todo'); if (t) { t.classList.add('plain'); t.textContent = 'Could not load your schedule. Reload the page.'; }
  });

  // Today in the course time zone (US Eastern), as YYYY-MM-DD
  const today = () => new Date(Date.now() - 5 * 3600000).toISOString().slice(0, 10);
  const sentKey = n => `sra.sent.w${n}`;
  const sentOn = n => { try { return localStorage.getItem(sentKey(n)); } catch (_) { return null; } };

  function submitUrl(me, n) {
    if (!me.site.homeworkForm) {
      // WhatsApp with the week and name already typed in
      const digits = String(me.site.whatsapp || '').replace(/\D/g, '');
      if (!digits) return me.site.whatsappLink || '#';
      return `https://wa.me/${digits}?text=${encodeURIComponent(`Week ${n} work from ${me.name.split(' ')[0]}:`)}`;
    }
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
      const sent = w.unlocked && sentOn(w.n);
      el.textContent = !w.unlocked ? `opens ${day(w.unlockDate)}` : isNow ? (sent ? `this week, sent ${day(sent)}` : 'this week') : sent ? `sent ${day(sent)}` : `class ${day(w.classDate)}`;
    });

    if (document.body.classList.contains('home')) home(me, nw, cur);

    // Week page
    $$('[data-week-date]').forEach(el => {
      const w = me.weeks.find(x => x.n === Number(el.dataset.weekDate));
      if (w) el.innerHTML = `class on<br><span class="big">${longDay(w.classDate)}</span>`;
    });
    $$('[data-submit]').forEach(a => {
      const n = a.dataset.submit;
      a.href = submitUrl(me, n);
      if (!me.site.homeworkForm) a.innerHTML = `Send week ${n} on WhatsApp <span class="arr" aria-hidden="true">→</span>`;
      const note = document.createElement('p');
      note.className = 'aside-note sent-note';
      const show = () => { const s = sentOn(n); note.textContent = s ? `You marked this week as sent on ${longDay(s)}.` : ''; };
      a.closest('p').after(note); show();
      a.addEventListener('click', () => { try { localStorage.setItem(sentKey(n), today()); } catch (_) {} show(); });
    });

    // The highlighted line on a week page follows the week: get ready before class, submit after it
    $$('[data-todo-week]').forEach(m => {
      const w = me.weeks.find(x => x.n === Number(m.dataset.todoWeek)); if (!w) return;
      const t = today();
      const due = new Date(new Date(`${w.classDate}T12:00:00Z`).getTime() + 6 * 86400000).toISOString().slice(0, 10);
      if (t <= w.classDate) m.innerHTML = `Before ${t === w.classDate ? 'class today' : longDay(w.classDate)}, get everything under <a href="#have-ready">Have ready for class</a> done.`;
      else if (t <= due) m.innerHTML = sentOn(w.n) ? `Sent. Swarit will review it. Next up: week ${w.n + 1}.` : `Do the tasks below and <a href="#submit">send them</a> by ${longDay(due)}, 8 PM Eastern.`;
      else m.innerHTML = sentOn(w.n) ? 'Done and sent. Look back here any time.' : `This week's work is due. <a href="#submit">Send it</a> as soon as you can.`;
      resweep(m);
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
