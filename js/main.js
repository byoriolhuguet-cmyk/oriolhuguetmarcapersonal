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
  const prog = d.querySelector('[data-progress]');
  const marq = $$('.marquee p');
  const hs = d.querySelector('[data-hs]'), hsTrack = hs && hs.querySelector('.services');
  const wide = matchMedia('(min-width: 1100px)');
  const bigs = $$('.big');
  let ticking = false, lastY = scrollY, skew = 0, vel = 0, dir = 1;
  // servicios en horizontal: posición suavizada y tarjetas que se enderezan al entrar
  let hsTarget = 0, hsCur = 0, hsRun = false;
  const hsCards = hs ? [...hs.querySelectorAll('.svc')] : [];
  const hsN = d.querySelector('[data-hs-n]'), hsBar = d.querySelector('[data-hs-bar]');
  const hsLoop = () => {
    hsCur += (hsTarget - hsCur) * 0.14;
    if (Math.abs(hsTarget - hsCur) < 0.0005) hsCur = hsTarget;
    const pin = hsTrack.parentElement, cs = getComputedStyle(pin);
    const travel = Math.max(0, hsTrack.scrollWidth - pin.clientWidth + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight));
    hsTrack.style.transform = `translate3d(${-hsCur * travel}px,0,0)`;
    const vw = innerWidth;
    hsCards.forEach(c => {
      const r = c.getBoundingClientRect(), k = Math.max(-1, Math.min(1, (r.left + r.width / 2 - vw / 2) / vw));
      const t = Math.max(0, k - 0.15);
      c.style.transform = `translate3d(0,${t * 60}px,0) rotate(${t * 7}deg) scale(${1 - t * 0.12})`;
    });
    hsN.textContent = String(Math.min(hsCards.length, 1 + Math.round(hsCur * (hsCards.length - 1)))).padStart(2, '0');
    hsBar.style.transform = `scaleX(${hsCur})`;
    if (hsCur !== hsTarget) requestAnimationFrame(hsLoop); else hsRun = false;
  };
  const onScroll = () => {
    ticking = false;
    const y = scrollY, vh = innerHeight;
    prog.style.transform = `scaleX(${y / Math.max(1, d.documentElement.scrollHeight - vh)})`;
    if (y !== lastY) dir = y > lastY ? 1 : -1;
    vel = Math.min(30, Math.abs(y - lastY));
    if (!reduce && hs && wide.matches) {
      const r = hs.getBoundingClientRect();
      hsTarget = Math.max(0, Math.min(1, -r.top / Math.max(1, r.height - vh)));
      if (!hsRun) { hsRun = true; requestAnimationFrame(hsLoop); }
    } else if (hsTrack && hsTrack.style.transform) {
      hsTrack.style.transform = ''; hsCards.forEach(c => (c.style.transform = ''));
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
    if (!reduce && hero) {
      // la foto sube desde abajo mientras el escenario está fijado; luego se queda quieta
      const p = Math.min(1, y / (vh * 0.65)), e = 1 - Math.pow(1 - p, 3);
      hero.style.setProperty('--rev', ((1 - e) * 100).toFixed(2));
      names.forEach(n => {
        n.style.transform = `translate3d(0,${-e * 4}vh,0) scale(${1 - e * 0.06})`;
        if (innerWidth > 700) n.style.fontStretch = 125 - e * 30 + '%';
      });
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

  // La carga se puede saltar con un toque o una tecla
  const loader = d.querySelector('.loader');
  if (loader) {
    const skip = () => d.documentElement.classList.add('ld-skipnow');
    loader.addEventListener('click', skip);
    addEventListener('keydown', skip, { once: true });
  }

  // Compartir el perfil (menú nativo en móvil, copiar enlace en escritorio)
  const share = d.querySelector('[data-share]');
  if (share) share.addEventListener('click', async () => {
    const data = { title: 'Oriol Huguet', text: 'Especialista en IA, marketing deportivo, digital retail y e-commerce', url: location.origin + '/' };
    try {
      if (navigator.share) await navigator.share(data);
      else { await navigator.clipboard.writeText(data.url); share.firstChild.textContent = 'Enlace copiado '; setTimeout(() => (share.firstChild.textContent = 'Compartir perfil '), 2000); }
    } catch (e) {}
  });

  // Menú móvil
  const burger = d.querySelector('[data-burger]'), mm = d.querySelector('[data-mmenu]');
  if (burger && mm) {
    const set = open => {
      burger.setAttribute('aria-expanded', open);
      burger.querySelector('.sr').textContent = open ? 'Cerrar menú' : 'Abrir menú';
      if (open) { mm.hidden = false; requestAnimationFrame(() => requestAnimationFrame(() => mm.classList.add('open'))); }
      else { mm.classList.remove('open'); setTimeout(() => { if (!mm.classList.contains('open')) mm.hidden = true; }, 450); }
      d.documentElement.style.overflow = open ? 'hidden' : '';
    };
    burger.addEventListener('click', () => set(burger.getAttribute('aria-expanded') !== 'true'));
    mm.addEventListener('click', e => { if (e.target.closest('a')) set(false); });
    addEventListener('keydown', e => { if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') { set(false); burger.focus(); } });
  }

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

  // Rayos X: foco que revela la versión pop-art de la foto (ratón y dedo)
  const xray = d.querySelector('[data-xray]');
  if (xray && !reduce) {
    const img = new Image();
    img.decoding = 'async';
    // la imagen se pide con la primera interacción, sin competir con la carga inicial
    const getX = () => {
      if (img.src) return;
      img.src = innerWidth > 1300 ? 'assets/img/oriol-xray-1240.avif' : 'assets/img/oriol-xray-860.avif';
      img.onload = () => (xray.style.backgroundImage = `url(${img.src})`);
    };
    ['pointermove', 'touchstart', 'scroll', 'keydown'].forEach(ev => addEventListener(ev, getX, { once: true, passive: true }));
    const spot = (x, y) => {
      const r = xray.getBoundingClientRect();
      xray.style.setProperty('--sx', x - r.left + 'px'); xray.style.setProperty('--sy', y - r.top + 'px');
      xray.classList.add('on');
    };
    hero.addEventListener('pointermove', e => { if (e.pointerType === 'mouse') spot(e.clientX, e.clientY); });
    hero.addEventListener('pointerleave', e => { if (e.pointerType === 'mouse') xray.classList.remove('on'); });
    let off;
    const touch = e => { const t = e.touches[0]; if (!t) return; clearTimeout(off); spot(t.clientX, t.clientY); };
    hero.addEventListener('touchstart', touch, { passive: true });
    hero.addEventListener('touchmove', touch, { passive: true });
    hero.addEventListener('touchend', () => { off = setTimeout(() => xray.classList.remove('on'), 900); }, { passive: true });
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
    const pad = e.wheelDeltaY ? Math.abs(e.wheelDeltaY) !== 120 && e.wheelDeltaY % 120 !== 0 : e.deltaMode === 0 && Math.abs(e.deltaY) < 50;
    if (pad) { smooth = false; return; }
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

  // Parallax del hero con el ratón
  if (hero) hero.addEventListener('pointermove', e => {
    const x = e.clientX / innerWidth - .5, y = e.clientY / innerHeight - .5;
    photo.style.setProperty('--mx', x * 18 + 'px'); photo.style.setProperty('--my', y * 10 + 'px');
    if (xray) { xray.style.setProperty('--mx', x * 18 + 'px'); xray.style.setProperty('--my', y * 10 + 'px'); }
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
