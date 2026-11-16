// Calendly incrustado: se carga después de la página y cambia según el tipo de sesión.
(() => {
  const d = document, box = d.querySelector('[data-cal]');
  if (!box) return;
  const frame = box.querySelector('iframe'), wrap = box.querySelector('.bk-frame');
  const types = [...box.querySelectorAll('.bk-type')];
  const direct = box.querySelector('[data-cal-direct]');
  let current = types[0] && types[0].dataset.type, started = false;

  const url = (type, inline = true) => {
    const p = new URLSearchParams({ utm_source: 'oriolhuguet.com', utm_medium: 'web', utm_campaign: box.dataset.placement || 'web' });
    if (inline) {
      p.set('embed_domain', location.hostname); p.set('embed_type', 'Inline'); p.set('hide_gdpr_banner', '1');
      p.set('hide_event_type_details', '1'); p.set('hide_landing_page_details', '1');
      p.set('primary_color', '00215e');
    }
    if (type) p.set('a1', type);
    return `${box.dataset.base}?${p.toString().replace(/\+/g, '%20')}`;
  };
  const load = () => {
    started = true;
    wrap.classList.remove('ready');
    frame.src = url(current);
    if (direct) direct.href = url(current, false);
  };
  frame.addEventListener('load', () => { if (frame.src) wrap.classList.add('ready'); });

  const sync = () => types.forEach(b => (b.tabIndex = b.getAttribute('aria-checked') === 'true' ? 0 : -1));
  const select = (type, focus) => {
    const t = types.find(b => b.dataset.type === type || b.dataset.key === type);
    if (!t) return;
    types.forEach(b => b.setAttribute('aria-checked', String(b === t)));
    sync();
    if (focus) t.focus({ preventScroll: true });
    if (t.dataset.type !== current || !started) { current = t.dataset.type; load(); }
  };
  types.forEach(b => b.addEventListener('click', () => select(b.dataset.type)));
  // Flechas para moverse entre tipos (patrón radiogroup)
  box.querySelector('.bk-types').addEventListener('keydown', e => {
    const n = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
    if (!n) return;
    e.preventDefault();
    const i = types.findIndex(b => b.getAttribute('aria-checked') === 'true');
    select(types[(i + n + types.length) % types.length].dataset.type, true);
  });
  sync();

  // Las tarjetas de reserva de la página llevan a este calendario en lugar de salir de la web
  d.querySelectorAll('a[data-book]').forEach(a => a.addEventListener('click', e => {
    e.preventDefault();
    select(a.dataset.book);
    box.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
  }));

  // Calendly pesa (~3,5 MB y cookies de terceros): se carga con el primer gesto del visitante
  // (mover el ratón, scroll, tocar o teclear) o al pulsar «Ver horas disponibles».
  const evs = ['pointermove', 'pointerdown', 'scroll', 'wheel', 'touchstart', 'keydown'];
  const first = () => { evs.forEach(ev => removeEventListener(ev, first)); if (!started) load(); };
  evs.forEach(ev => addEventListener(ev, first, { passive: true }));
  const btn = box.querySelector('[data-cal-show]');
  if (btn) btn.addEventListener('click', first);
})();
