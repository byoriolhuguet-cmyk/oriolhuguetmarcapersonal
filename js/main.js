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

  // Titulares: palabra a palabra con máscara
  if (!reduce) $$('.rvc,.giant-split').forEach(h => {
    let w = 0;
    const wrap = node => [...node.childNodes].forEach(n => {
      if (n.nodeType === 3) {
        const frag = d.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(t => {
          if (!t) return;
          if (/^\s+$/.test(t)) return frag.append(t);
          const m = d.createElement('span'), i = d.createElement('span');
          m.className = 'wm'; i.className = 'wi'; i.style.setProperty('--w', w++); i.textContent = t;
          m.append(i); frag.append(m);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1 && n.tagName !== 'BR') wrap(n);
    });
    wrap(h); h.classList.add('split');
  });

  // Etiquetas de sección que se «descifran»
  const glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&';
  const scramble = el => {
    const final = el.textContent; let f = 0;
    const run = () => {
      el.textContent = final.split('').map((c, i) => (c === ' ' || i < f / 2 ? c : glyphs[Math.random() * glyphs.length | 0])).join('');
      if (++f / 2 <= final.length) requestAnimationFrame(run); else el.textContent = final;
    };
    run();
  };
  const lio = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { scramble(e.target); lio.unobserve(e.target); } }));
  if (!reduce) $$('.sec-head .label').forEach(l => lio.observe(l));

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
  $$('.stg').forEach(g => [...g.children].forEach((c, i) => c.style.setProperty('--k', i)));
  $$('.rv,.rvc,.stg,[data-pitch],.giant').forEach(el => io.observe(el));
  // quitar el retardo escalonado tras la entrada para que el hover responda al instante
  $$('.stg').forEach(g => g.addEventListener('transitionend', () => setTimeout(() => [...g.children].forEach(c => c.style.setProperty('--k', 0)), 400), { once: true }));

  // Scroll: parallax del hero + manifiesto
  const photo = d.querySelector('[data-photo]');
  const names = $$('[data-hn]');
  const hero = d.querySelector('.hero');
  const xr = d.querySelector('[data-xray]');
  const prog = d.querySelector('[data-progress]');
  const marq = $$('.marquee p');
  const hs = d.querySelector('[data-hs]'), hsTrack = hs && hs.querySelector('.services');
  const wide = matchMedia('(min-width: 1100px)');
  const bigs = $$('.big');
  let ticking = false, lastY = scrollY, skew = 0, vel = 0, dir = 1;
  const onScroll = () => {
    ticking = false;
    const y = scrollY, vh = innerHeight;
    prog.style.transform = `scaleX(${y / Math.max(1, d.documentElement.scrollHeight - vh)})`;
    if (y !== lastY) dir = y > lastY ? 1 : -1;
    vel = Math.min(30, Math.abs(y - lastY));
    if (!reduce && hs && wide.matches) {
      const r = hs.getBoundingClientRect();
      hsTrack.style.setProperty('--hp', Math.max(0, Math.min(1, -r.top / Math.max(1, r.height - vh))).toFixed(4));
    }
    if (!reduce) bigs.forEach(bg => {
      const r = bg.getBoundingClientRect();
      if (r.bottom > 0 && r.top < vh) bg.style.setProperty('--tx', ((r.top + r.height / 2) / vh - .5) * -60 + 'px');
    });
    if (!reduce) {
      skew = Math.max(-12, Math.min(12, (y - lastY) * 0.4));
      marq.forEach(m => (m.style.transform = `skewX(${-skew}deg)`));
      clearTimeout(onScroll.t);
      onScroll.t = setTimeout(() => marq.forEach(m => (m.style.transform = '')), 120);
    }
    lastY = y;
    if (!reduce && y < vh * 1.2 && innerWidth > 700) {
      photo.style.setProperty('--py', y * 0.18 + 'px');
      if (xr) xr.style.setProperty('--py', y * 0.18 + 'px');
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

  // Cinta: cambia de sentido con el scroll y acelera con la velocidad
  const track = d.querySelector('.marquee-track');
  if (track && !reduce) {
    let x = 0, vis = true;
    track.style.animation = 'none';
    new IntersectionObserver(([e]) => (vis = e.isIntersecting)).observe(track);
    const loop = () => {
      if (vis) {
        const half = track.scrollWidth / 2;
        x -= (0.6 + vel * 0.25) * dir;
        vel *= 0.9;
        if (x <= -half) x += half; else if (x > 0) x -= half;
        track.style.transform = `translate3d(${x}px,0,0)`;
      }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  if (!fine || reduce) return;

  // Scroll suave con inercia (solo ratón)
  let target = scrollY, sy = scrollY, smooth = false;
  const maxY = () => d.documentElement.scrollHeight - innerHeight;
  const glide = () => {
    sy += (target - sy) * 0.1;
    if (Math.abs(target - sy) < 0.5) { sy = target; smooth = false; }
    scrollTo({ top: sy, behavior: 'instant' });
    if (smooth) requestAnimationFrame(glide);
  };
  addEventListener('wheel', e => {
    if (e.ctrlKey || e.defaultPrevented) return;
    e.preventDefault();
    if (!smooth) { target = sy = scrollY; }
    target = Math.max(0, Math.min(maxY(), target + e.deltaY * (e.deltaMode === 1 ? 40 : 1)));
    if (!smooth) { smooth = true; requestAnimationFrame(glide); }
  }, { passive: false });

  // Cursor
  const cur = d.querySelector('[data-cursor]');
  addEventListener('pointermove', e => { cur.style.transform = `translate3d(${e.clientX}px,${e.clientY}px,0)`; }, { passive: true });
  $$('a,button,.job,.club,.svc').forEach(el => {
    el.addEventListener('pointerenter', () => cur.classList.add('big'));
    el.addEventListener('pointerleave', () => cur.classList.remove('big'));
  });

  // Rayos X: foco que revela la versión pop-art de la foto
  const xray = d.querySelector('[data-xray]');
  if (xray) {
    const img = new Image();
    img.decoding = 'async';
    const load = () => {
      img.src = innerWidth > 1300 ? 'assets/img/oriol-xray-1240.avif' : 'assets/img/oriol-xray-860.avif';
      img.onload = () => (xray.style.backgroundImage = `url(${img.src})`);
    };
    addEventListener('load', () => setTimeout(load, 2500), { once: true });
    hero.addEventListener('pointerenter', () => xray.classList.add('on'));
    hero.addEventListener('pointerleave', () => xray.classList.remove('on'));
  }

  // Parallax del hero con el ratón
  if (hero) hero.addEventListener('pointermove', e => {
    const x = e.clientX / innerWidth - .5, y = e.clientY / innerHeight - .5;
    photo.style.setProperty('--mx', x * 18 + 'px'); photo.style.setProperty('--my', y * 10 + 'px');
    if (xray) {
      xray.style.setProperty('--mx', x * 18 + 'px'); xray.style.setProperty('--my', y * 10 + 'px');
      const r = xray.getBoundingClientRect();
      xray.style.setProperty('--sx', e.clientX - r.left + 'px'); xray.style.setProperty('--sy', e.clientY - r.top + 'px');
    }
    names.forEach(n => { n.style.setProperty('--mx', x * -30 + 'px'); n.style.setProperty('--my', y * -14 + 'px'); });
  });

  // Botones magnéticos
  $$('[data-mag]').forEach(el => {
    el.addEventListener('pointermove', e => {
      const r = el.getBoundingClientRect();
      el.style.translate = `${(e.clientX - r.left - r.width / 2) * .3}px ${(e.clientY - r.top - r.height / 2) * .35}px`;
    });
    el.addEventListener('pointerleave', () => (el.style.translate = '0 0'));
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
