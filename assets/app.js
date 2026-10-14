// Fills in the parts of each page that depend on who is signed in: dates, locks, next class, links.
(function () {
  const $ = s => document.querySelector(s);
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const day = d => new Date(`${d}T12:00:00Z`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  const longDay = d => new Date(`${d}T12:00:00Z`).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
  const pad = n => String(n).padStart(2, '0');

  // Copy buttons on fill-in templates
  document.querySelectorAll('.tpl .copy').forEach(b => b.addEventListener('click', () => {
    const t = b.parentElement.querySelector('code').innerText;
    const done = l => { b.textContent = l; setTimeout(() => (b.textContent = 'Copy'), 1500); };
    (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(() => done('Copied'), () => done('Select and copy'));
  }));

  const params = new URLSearchParams(location.search);
  const cohortParam = params.get('cohort');
  fetch('/api/me' + (cohortParam ? `?cohort=${encodeURIComponent(cohortParam)}` : ''), { credentials: 'same-origin' })
    .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
    .then(render)
    .catch(() => { const h = $('#nextClass .big'); if (h) h.textContent = 'Could not load your schedule. Reload the page.'; });

  function weekRow(w, me) {
    const cls = !w.unlocked ? 'locked' : w.n === me.next ? 'now' : '';
    const when = !w.unlocked ? `Opens ${day(w.unlockDate)}` : `Class ${day(w.classDate)}`;
    return `<li data-week="${w.n}" class="${cls}"><a href="${w.url}"><span class="num">${pad(w.n)}</span><span class="t"><b>${esc(w.title)}</b><small>${esc(w.kit)}</small></span><span class="when">${w.n === me.next && w.unlocked ? 'This week' : when}</span></a></li>`;
  }

  function submitUrl(me, n) {
    if (!me.site.homeworkForm) return me.site.whatsappLink || '#';
    const u = new URL(me.site.homeworkForm);
    u.searchParams.set('week', n);
    u.searchParams.set('student', me.name);
    return u.toString();
  }

  function render(me) {
    // Home
    if (document.body.classList.contains('home')) {
      $('#hello').textContent = `Hi ${me.name.split(' ')[0]}`;
      $('#cohortLabel').textContent = me.cohortLabel;
      if (me.admin && me.cohorts) {
        $('#cohortPick').innerHTML = `<div class="cohortpick">${me.cohorts.map(c => `<button data-c="${c.key}" class="${c.key === me.cohort ? 'on' : ''}">${esc(c.label)}</button>`).join('')}<a class="btn" style="padding:5px 14px;font-size:14px" href="/students/">Students</a></div>`;
        document.querySelectorAll('.cohortpick button').forEach(b => b.onclick = () => { location.search = `?cohort=${b.dataset.c}`; });
      }
      const nw = me.weeks.find(w => w.n === me.next);
      const time = me.site.classTime || 'time confirmed before class one';
      $('#nextClass').innerHTML = nw
        ? `<span class="lab">Next class · Week ${nw.n}</span><p class="big">${longDay(nw.classDate)}</p><p class="small">${esc(time)}</p>${me.site.meetLink ? `<a class="btn" href="${esc(me.site.meetLink)}" target="_blank" rel="noopener">Join the class ›</a>` : '<p class="small">The class link appears here before class one.</p>'}`
        : `<span class="lab">Course</span><p class="big">All 12 weeks done</p><p class="small">Well done.</p>`;
      const open = me.weeks.filter(w => w.unlocked);
      const cur = nw && nw.unlocked ? nw : open[open.length - 1];
      $('#thisWeek').innerHTML = cur
        ? `<span class="lab">This week · Week ${cur.n}</span><p class="big">${esc(cur.title)}</p><p class="small">${esc(cur.kit)}</p><a class="btn" href="${cur.url}">Open week ${cur.n} ›</a>`
        : `<span class="lab">This week</span><p class="big">Week 1 opens ${day(me.weeks[0].unlockDate)}</p><p class="small">Get ready: install phyphox on a phone and Arduino IDE 2 on your laptop.</p><a class="btn" href="/resources/getting-started/">How the course works ›</a>`;
      const one = $('#oneOnOne');
      if (me.site.oneOnOneLink) { one.href = me.site.oneOnOneLink; one.target = '_blank'; }
      else { one.href = me.site.whatsappLink; one.target = '_blank'; one.querySelector('span').textContent = 'Message Swarit to book'; }
      $('#homeWeeks').innerHTML = me.weeks.map(w => weekRow(w, me)).join('');
    }

    // Weeks index
    document.querySelectorAll('[data-week-when]').forEach(el => {
      const w = me.weeks.find(x => x.n === Number(el.dataset.weekWhen)); if (!w) return;
      const li = el.closest('li');
      li.className = !w.unlocked ? 'locked' : w.n === me.next ? 'now' : '';
      el.textContent = !w.unlocked ? `Opens ${day(w.unlockDate)}` : w.n === me.next ? 'This week' : `Class ${day(w.classDate)}`;
    });

    // Week page
    document.querySelectorAll('[data-week-date]').forEach(el => {
      const w = me.weeks.find(x => x.n === Number(el.dataset.weekDate));
      if (w) el.textContent = `Class ${longDay(w.classDate)}`;
    });
    document.querySelectorAll('[data-submit]').forEach(a => {
      a.href = submitUrl(me, a.dataset.submit);
      if (!me.site.homeworkForm) a.textContent = 'Send your work on WhatsApp ›';
    });
  }
})();
