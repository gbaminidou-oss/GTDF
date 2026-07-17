/* GTDF Platform — Main JavaScript */

/* ── Flash message auto-dismiss ─────────────────────────── */
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s ease, transform .4s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-8px)';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

/* ── Mobile sidebar toggle ──────────────────────────────── */
const menuBtn = document.getElementById('menu-toggle');
const sidebar = document.querySelector('.sidebar');
if (menuBtn && sidebar) {
  menuBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== menuBtn) {
      sidebar.classList.remove('open');
    }
  });
}

/* ── Countdown timer for scenarios ─────────────────────── */
function startTimer(seconds, displayId, formId) {
  const display = document.getElementById(displayId);
  if (!display) return;
  let remaining = seconds;

  const interval = setInterval(() => {
    remaining--;
    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    display.textContent = `${m}:${s.toString().padStart(2, '0')}`;

    if (remaining <= 30) display.classList.add('warning');
    if (remaining <= 10) { display.classList.remove('warning'); display.classList.add('danger'); }

    if (remaining <= 0) {
      clearInterval(interval);
      const form = document.getElementById(formId);
      if (form) form.submit();
    }
  }, 1000);
}

/* ── Answer option highlight ────────────────────────────── */
document.querySelectorAll('.answer-option').forEach(opt => {
  opt.addEventListener('click', () => {
    const name = opt.querySelector('input')?.name;
    if (name) {
      document.querySelectorAll(`input[name="${name}"]`).forEach(inp => {
        inp.closest('.answer-option')?.classList.remove('selected');
      });
    }
    opt.classList.add('selected');
    const inp = opt.querySelector('input[type=radio]');
    if (inp) inp.checked = true;
  });
});

/* ── Assessment form validation ─────────────────────────── */
const assessmentForm = document.getElementById('assessment-form');
if (assessmentForm) {
  assessmentForm.addEventListener('submit', e => {
    const groups = {};
    assessmentForm.querySelectorAll('input[type=radio]').forEach(inp => {
      if (!groups[inp.name]) groups[inp.name] = false;
      if (inp.checked) groups[inp.name] = true;
    });
    const unanswered = Object.values(groups).filter(v => !v).length;
    if (unanswered > 0) {
      e.preventDefault();
      alert(`Please answer all questions. ${unanswered} question(s) remaining.`);
    }
  });
}

/* ── Smooth scroll for landing page anchors ─────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});

/* ── XP bar animation on load ───────────────────────────── */
document.querySelectorAll('.xp-fill[data-pct]').forEach(bar => {
  const pct = bar.dataset.pct;
  bar.style.width = '0%';
  requestAnimationFrame(() => {
    setTimeout(() => { bar.style.transition = 'width .8s ease'; bar.style.width = pct + '%'; }, 100);
  });
});

/* ── Progress fill animation ────────────────────────────── */
document.querySelectorAll('.progress-fill[data-pct]').forEach(bar => {
  const pct = bar.dataset.pct;
  bar.style.width = '0%';
  requestAnimationFrame(() => {
    setTimeout(() => { bar.style.transition = 'width .8s ease'; bar.style.width = pct + '%'; }, 200);
  });
});
