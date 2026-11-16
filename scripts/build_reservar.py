#!/usr/bin/env python3
"""Genera /reservar/ y coloca las zonas de reserva en la portada.

Uso: python3 scripts/build_reservar.py   (después de build_blog.py y build_newsletter.py)
"""
import re
from pathlib import Path

from booking import CSS as BOOK_CSS, DURATION, cards
from build_blog import NAV, WA, WA_URL, SITE, person_ld
from build_newsletter import FOOT, page_head

ROOT = Path(__file__).resolve().parent.parent
SUB = "Consultorías, mentorías y reuniones para puestos de trabajo. Gratis, por videollamada y a la hora que mejor te venga."

PAGE_CSS = BOOK_CSS + '''
.rs-hero{position:relative;overflow:hidden;background:radial-gradient(60% 70% at 85% 10%,var(--brand-2) 0%,transparent 70%),linear-gradient(rgba(243,245,250,.03) 1px,transparent 1px) 0 0/56px 56px,linear-gradient(90deg,rgba(243,245,250,.03) 1px,transparent 1px) 0 0/56px 56px,var(--brand);color:var(--paper);padding:clamp(110px,14vh,150px) var(--pad) clamp(50px,8vh,90px)}
.rs-hero::before{content:"";position:absolute;right:7vw;top:-20%;height:140%;width:clamp(12px,1.4vw,22px);background:var(--accent);transform:rotate(16deg)}
.rs-hero::after{content:"";position:absolute;right:calc(7vw - clamp(26px,3vw,48px));top:-20%;height:140%;width:2px;background:var(--paper);opacity:.8;transform:rotate(16deg)}
.rs-hero>*{position:relative;z-index:1}
.rs-head{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:clamp(24px,5vw,70px);align-items:end;margin-bottom:clamp(30px,5vh,52px)}
.rs-eyebrow{display:inline-flex;align-items:center;gap:.6em;padding:7px 14px;border-radius:999px;border:1px solid currentColor;color:var(--accent);font-size:.68rem;font-weight:800;letter-spacing:.22em;text-transform:uppercase}
.rs-eyebrow::before{content:"";width:.55em;height:.55em;border-radius:50%;background:currentColor;animation:rsping 2s infinite}
@keyframes rsping{70%{box-shadow:0 0 0 8px rgba(255,199,44,0)}0%{box-shadow:0 0 0 0 rgba(255,199,44,.7)}}
.rs-hero h1{margin-top:20px;font-size:clamp(2.8rem,7vw,6.6rem);font-weight:900;font-stretch:110%;line-height:.9;letter-spacing:-.05em;text-wrap:balance}
.rs-hero h1 em{font-family:"Instrument Serif",Georgia,serif;font-style:italic;font-weight:400;font-stretch:100%;color:var(--accent);letter-spacing:-.03em;padding-right:.04em}
.rs-side p{color:#c9d1e6;font-size:clamp(1.02rem,1.3vw,1.2rem);line-height:1.5;max-width:40ch}
.rs-who{display:flex;align-items:center;gap:14px;margin-top:18px}
.rs-who img{width:52px;height:52px;border-radius:16px;border:2px solid var(--accent)}
.rs-who span{font-size:.88rem;color:#b8c2da;line-height:1.35}
.rs-who b{display:block;color:var(--paper);font-size:.98rem}
.rs-facts{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px;list-style:none;padding:0}
.rs-facts li{padding:7px 12px;border-radius:999px;background:rgba(243,245,250,.08);border:1px solid rgba(243,245,250,.12);font-size:.8rem;font-weight:700}
.rs-hero .bk-card{background:linear-gradient(180deg,rgba(0,14,43,.75),rgba(0,14,43,.92))}
@media (max-width:900px){.rs-head{grid-template-columns:1fr;align-items:start}.rs-hero::before,.rs-hero::after{display:none}}
.rs-sec{padding:clamp(80px,11vw,140px) var(--pad)}
.rs-sec h2{font-size:clamp(2.2rem,5.4vw,4.8rem);font-weight:800;line-height:.95;letter-spacing:-.05em;text-wrap:balance;margin-bottom:clamp(30px,5vw,56px)}
.rs-sec h2 em{font-family:"Instrument Serif",Georgia,serif;font-style:italic;font-weight:400;color:var(--brand-2);letter-spacing:-.02em}
.rs-steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:26px;counter-reset:s}
.rs-steps li{padding:26px 24px;border-radius:24px;background:#fff;box-shadow:0 0 0 6px rgba(0,33,94,.035),0 0 0 7px rgba(0,33,94,.09)}
.rs-steps li::before{counter-increment:s;content:"0" counter(s);display:block;font-size:3.4rem;font-weight:900;font-stretch:65%;line-height:.9;color:var(--brand-2)}
.rs-steps h3{margin-top:18px;font-size:1.3rem;font-weight:800;letter-spacing:-.02em}
.rs-steps p{margin-top:8px;color:#3a4766}
@media (max-width:860px){.rs-steps{grid-template-columns:1fr}}
.rs-final{background:var(--ink);color:var(--paper)}
.rs-final h2{color:var(--paper)}
.rs-final h2 em{color:var(--accent)}
.rs-alt{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-top:34px;color:#b8c2da;font-weight:600}
.rs-alt a{color:var(--paper);text-underline-offset:4px}
'''

WHO = '''<div class="rs-who"><img src="/assets/img/oriol-avatar.webp" width="160" height="160" alt="Oriol Huguet"><span><b>Oriol Huguet</b>IA · Marketing deportivo · Digital retail · E-commerce</span></div>'''


def reservar_page():
    url = f"{SITE}/reservar/"
    ld = [person_ld(), {"@type": "WebPage", "@id": url, "url": url, "name": "Reserva una sesión gratuita con Oriol Huguet",
                        "description": SUB, "inLanguage": "es", "about": {"@id": f"{SITE}/#oriol"}}]
    html = page_head("Reserva una sesión gratuita de 30 min | Oriol Huguet", SUB, url,
                     f"{SITE}/assets/img/og-oriol-huguet.jpg", ld, PAGE_CSS) + f'''
<body>
{NAV.format(cur="")}
<main id="main">
<section class="rs-hero" aria-labelledby="rs-title">
  <div class="rs-head">
    <div>
      <span class="rs-eyebrow">Agenda abierta · {DURATION} · Gratis</span>
      <h1 id="rs-title">Reserva <em>30 minutos</em> conmigo</h1>
    </div>
    <div class="rs-side">
      <p>{SUB}</p>
      {WHO}
    </div>
  </div>
  {cards("reservar-hero")}
  <ul class="rs-facts" aria-label="Detalles de la sesión"><li>Videollamada</li><li>Castellano, catalán o inglés</li><li>Sin compromiso</li><li>Confirmación al momento</li></ul>
</section>

<section class="rs-sec" aria-labelledby="rs-how">
  <h2 id="rs-how">Cómo <em>funciona</em></h2>
  <ol class="rs-steps">
    <li><h3>Elige el tipo de sesión</h3><p>Consultoría, mentoría o reunión para un puesto. Así llego preparado.</p></li>
    <li><h3>Escoge día y hora</h3><p>Te llevo a mi calendario de Calendly con los huecos libres en tu zona horaria.</p></li>
    <li><h3>Recibe el enlace</h3><p>Te llega la invitación con la videollamada. Si te surge algo, la cambias desde el mismo email.</p></li>
  </ol>
</section>

<section class="rs-sec rs-final" aria-labelledby="rs-end">
  <h2 id="rs-end">¿Reservamos tu <em>hora?</em></h2>
  {cards("reservar-final", compact=True)}
  <p class="rs-alt">¿Prefieres escribirme antes? <a href="{WA_URL}" target="_blank" rel="noopener">WhatsApp</a> · <a href="mailto:byoriolhuguet@gmail.com">byoriolhuguet@gmail.com</a></p>
</section>
</main>
{FOOT}
{WA}
<script src="/js/newsletter.js" defer></script>
</body>
</html>
'''
    (ROOT / "reservar").mkdir(exist_ok=True)
    (ROOT / "reservar" / "index.html").write_text(html)


def inject(path, marker, content, css=False):
    p = ROOT / path
    s = p.read_text()
    a, b = (f"/* {marker}:start */", f"/* {marker}:end */") if css else (f"<!-- {marker}:start -->", f"<!-- {marker}:end -->")
    pat = re.compile(re.escape(a) + ".*?" + re.escape(b), re.S)
    if not pat.search(s):
        raise SystemExit(f"Faltan los marcadores {marker} en {path}")
    p.write_text(pat.sub(lambda m: a + content + b, s))


def main():
    reservar_page()
    inject("index.html", "book-css", BOOK_CSS, css=True)
    inject("index.html", "book-end", cards("home-final"))
    print("reservar y portada actualizados")


if __name__ == "__main__":
    main()
