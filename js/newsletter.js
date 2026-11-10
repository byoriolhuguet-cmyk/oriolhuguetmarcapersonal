// Punto Muerto: formularios de suscripción y pop-up.
(() => {
  const d = document;
  const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const DAY = 864e5;
  const store = {
    get: k => localStorage.getItem(k), // puede lanzar: quien llama lo controla
    set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* sin almacenamiento: no pasa nada */ } },
  };

  // ---------- Formulario ----------
  const bind = form => {
    if (form.dataset.bound) return;
    form.dataset.bound = '1';
    const source = form.dataset.source || 'page';
    const name = form.elements.first_name, email = form.elements.email, consent = form.elements.consent;
    const btn = form.querySelector('button[type="submit"]'), label = btn.querySelector('.nl-btn-t');
    const msg = form.querySelector('.nl-msg');
    const fail = (text, field) => {
      msg.textContent = text;
      msg.classList.add('is-error');
      if (field) { field.setAttribute('aria-invalid', 'true'); field.focus(); }
    };
    [name, email, consent].forEach(f => f.addEventListener('input', () => f.removeAttribute('aria-invalid')));

    form.addEventListener('submit', async e => {
      e.preventDefault();
      msg.textContent = ''; msg.classList.remove('is-error');
      const n = name.value.trim(), m = email.value.trim();
      if (!n || n.length > 60) return fail('Escribe tu nombre (máximo 60 caracteres).', name);
      if (!EMAIL.test(m)) return fail('Revisa tu email, parece que falta algo.', email);
      if (!consent.checked) return fail('Necesito que aceptes recibir la newsletter para poder enviártela.', consent);

      btn.disabled = true; label.textContent = 'Enviando…';
      try {
        const r = await fetch('/api/subscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ first_name: n, email: m, source, website: form.elements.website.value }),
        });
        const data = await r.json().catch(() => ({}));
        if (!r.ok || !data.ok) throw new Error(data.error || 'Algo ha fallado, inténtalo de nuevo');
        store.set('pm_subscribed', '1');
        if (typeof window.va === 'function') window.va('event', { name: 'newsletter_subscribe', data: { source } });
        const ok = d.createElement('div');
        ok.className = 'nl-ok';
        ok.setAttribute('role', 'status');
        ok.tabIndex = -1;
        ok.textContent = `¡Dentro, ${n}! Nos vemos el domingo a las 17:00.`;
        form.replaceWith(ok);
        ok.focus();
      } catch (err) {
        fail(err.message || 'Algo ha fallado, inténtalo de nuevo');
        btn.disabled = false; label.textContent = 'Quiero recibirla';
      }
    });
  };
  d.querySelectorAll('[data-nl-form]').forEach(bind);

  // ---------- Pop-up ----------
  const path = location.pathname;
  const tpl = d.getElementById('nl-popup-tpl');
  if (!tpl || /^\/(newsletter|privacidad)(\/|$)/.test(path)) return;
  try {
    if (store.get('pm_subscribed') === '1') return;
    const closed = +store.get('pm_popup_closed_at') || 0;
    if (closed && Date.now() - closed < 30 * DAY) return;
  } catch (e) { return; } // sin localStorage no molestamos con el pop-up

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const css = () => new Promise(res => {
    if (d.querySelector('link[data-nl-css]')) return res();
    const l = d.createElement('link');
    l.rel = 'stylesheet'; l.href = '/css/newsletter.css'; l.dataset.nlCss = '';
    l.onload = l.onerror = res;
    d.head.append(l);
  });

  const t0 = Date.now();
  let shown = false, timer;
  const show = async () => {
    if (shown) return;
    // nunca antes de 5 s en la página
    const wait = 5000 - (Date.now() - t0);
    if (wait > 0) { clearTimeout(timer); timer = setTimeout(show, wait); return; }
    if (d.querySelector('[data-mmenu].open')) return; // no interrumpir el menú móvil
    shown = true; cleanup();
    await css();
    open();
  };

  const open = () => {
    const pop = tpl.content.firstElementChild.cloneNode(true);
    d.body.append(pop);
    bind(pop.querySelector('[data-nl-form]'));
    const card = pop.querySelector('.nl-pop-card');
    const before = d.activeElement;
    const focusables = () => [...card.querySelectorAll('a[href],button:not([disabled]),input:not([tabindex="-1"]),[tabindex="0"]')].filter(el => el.offsetParent !== null || el === d.activeElement);
    const close = () => {
      if (!pop.querySelector('.nl-ok')) store.set('pm_popup_closed_at', String(Date.now()));
      pop.classList.remove('open');
      d.removeEventListener('keydown', onKey);
      setTimeout(() => pop.remove(), reduce ? 0 : 500);
      if (before && before.focus) before.focus({ preventScroll: true });
    };
    const onKey = e => {
      if (e.key === 'Escape') { e.preventDefault(); close(); return; }
      if (e.key !== 'Tab') return;
      const f = focusables(); if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); }
      else if (!card.contains(d.activeElement)) { e.preventDefault(); first.focus(); }
    };
    pop.querySelector('.nl-pop-x').addEventListener('click', close);
    pop.querySelector('.nl-pop-bg').addEventListener('click', close);
    d.addEventListener('keydown', onKey);
    pop.hidden = false;
    requestAnimationFrame(() => requestAnimationFrame(() => pop.classList.add('open')));
    setTimeout(() => pop.querySelector('input[name="first_name"]').focus({ preventScroll: true }), reduce ? 0 : 350);
  };

  // Disparadores: 50 % de scroll, intención de salida (escritorio) o 25 s.
  const onScroll = () => {
    const max = d.documentElement.scrollHeight - innerHeight;
    if (max > 0 && scrollY / max >= 0.5) show();
  };
  const onOut = e => { if (!e.relatedTarget && e.clientY <= 0) show(); };
  const fine = matchMedia('(pointer: fine)').matches;
  addEventListener('scroll', onScroll, { passive: true });
  if (fine) d.addEventListener('mouseout', onOut);
  const t25 = setTimeout(show, 25000);
  function cleanup() {
    removeEventListener('scroll', onScroll);
    d.removeEventListener('mouseout', onOut);
    clearTimeout(t25);
  }
})();
