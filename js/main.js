(() => {
  const d = document, b = d.body;
  b.classList.remove('no-js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;
  const $$ = (s, r = d) => [...r.querySelectorAll(s)];

  // Reloj de Barcelona
  const clocks = $$('[data-clock]');
  const fmt = new Intl.DateTimeFormat('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });
  const tick = () => clocks.forEach(c => (c.textContent = 'BCN ' + fmt.format(new Date())));
  tick(); setInterval(tick, 30000);

  // Manifiesto: las palabras se encienden al hacer scroll
  const man = d.querySelector('[data-words]');
  let words = [];
  if (man) {
    const walk = (node, hl) => {
      [...node.childNodes].forEach(n => {
        if (n.nodeType === 3) {
          const frag = d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(t => {
            if (!t) return;
            if (/^\s+$/.test(t)) return frag.append(t);
            const s = d.createElement('span');
            s.className = hl ? 'w hl' : 'w';
            s.textContent = t;
            frag.append(s);
          });
          n.replaceWith(frag);
        } else walk(n, hl || n.tagName === 'EM');
      });
    };
    walk(man, false);
    words = $$('.w', man);
  }

  // Revelado de bloques y contadores
  const count = el => {
    const end = +el.dataset.count, start = end > 1000 ? end - 40 : 0, t0 = performance.now();
    const step = t => {
      const p = Math.min(1, (t - t0) / 1400), e = 1 - Math.pow(1 - p, 4);
      el.textContent = Math.round(start + (end - start) * e);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in');
    const n = e.target.querySelector('[data-count]');
    if (n && !reduce) count(n);
    io.unobserve(e.target);
  }), { rootMargin: '0px 0px -12% 0px' });
  $$('.rv').forEach(el => io.observe(el));

  // Scroll: parallax del hero + manifiesto
  const photo = d.querySelector('[data-photo]');
  const names = $$('[data-hn]');
  const hero = d.querySelector('.hero');
  let ticking = false;
  const onScroll = () => {
    ticking = false;
    const y = scrollY, vh = innerHeight;
    if (!reduce && y < vh * 1.2 && innerWidth > 700) {
      photo.style.setProperty('--py', y * 0.18 + 'px');
      const s = Math.max(62, 125 - y / vh * 70);
      names.forEach(n => { n.style.fontStretch = s + '%'; n.style.transform = `translate3d(0,${y * 0.35}px,0)`; });
    }
    if (words.length) {
      const r = man.getBoundingClientRect();
      const p = (vh * 0.85 - r.top) / (r.height + vh * 0.25);
      const on = Math.round(Math.max(0, Math.min(1, p)) * words.length);
      words.forEach((w, i) => w.classList.toggle('on', i < on));
    }
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  if (hero) onScroll();

  // Copiar email
  const copy = d.querySelector('[data-copy]');
  if (copy && navigator.clipboard) {
    copy.hidden = false;
    copy.addEventListener('click', () => navigator.clipboard.writeText(copy.dataset.copy).then(() => {
      copy.textContent = '¡Copiado! ✓';
      setTimeout(() => (copy.textContent = 'Copiar email'), 2000);
    }));
  }

  if (!fine || reduce) return;

  // Cursor
  const cur = d.querySelector('[data-cursor]');
  addEventListener('pointermove', e => { cur.style.transform = `translate3d(${e.clientX}px,${e.clientY}px,0)`; }, { passive: true });
  $$('a,button,.job,.club,.svc').forEach(el => {
    el.addEventListener('pointerenter', () => cur.classList.add('big'));
    el.addEventListener('pointerleave', () => cur.classList.remove('big'));
  });

  // Logo que sigue al cursor en la trayectoria
  const fol = d.querySelector('[data-follow]');
  $$('.job').forEach(job => {
    job.addEventListener('pointerenter', () => {
      const src = job.dataset.logo;
      fol.innerHTML = src ? `<img src="${src}" alt="">` : `<b>${job.dataset.mono}</b>`;
      fol.classList.add('on');
    });
    job.addEventListener('pointerleave', () => fol.classList.remove('on'));
    job.addEventListener('pointermove', e => {
      fol.style.setProperty('--fx', e.clientX + 30 + 'px');
      fol.style.setProperty('--fy', e.clientY - 85 + 'px');
    });
  });

  // Ficha de jugador con relieve
  const card = d.querySelector('[data-card] .card-in');
  if (card) {
    card.addEventListener('pointermove', e => {
      const r = card.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      card.style.setProperty('--ry', (x - .5) * 18 + 'deg');
      card.style.setProperty('--rx', (.5 - y) * 18 + 'deg');
      card.style.setProperty('--mx', x * 100 + '%');
      card.style.setProperty('--my', y * 100 + '%');
    });
    card.addEventListener('pointerleave', () => { card.style.setProperty('--rx', '0deg'); card.style.setProperty('--ry', '0deg'); });
  }
})();
