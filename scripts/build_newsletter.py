#!/usr/bin/env python3
"""Genera /newsletter/ y /privacidad/, la imagen OG de Punto Muerto y coloca el
formulario y el pop-up de la newsletter en la portada y en /cv/.

Uso: python3 scripts/build_newsletter.py   (requiere pillow y fonttools, como build_blog.py)
"""
import json
import re
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from build_blog import NAV, WA, WA_URL, SITE, head, person_ld
from newsletter_form import form_html, popup_template

ROOT = Path(__file__).resolve().parent.parent
NL_CSS = (ROOT / "css" / "newsletter.css").read_text()
SUB = "La inteligencia artificial está cambiando el deporte. Cada domingo te cuento cómo, en 5 minutos."
SCRIPTS = '<script src="/js/newsletter.js" defer></script>'

PAGE_CSS = '''
.nl-split{display:grid;grid-template-columns:1fr 1fr;min-height:100svh;background:var(--ink);color:var(--paper)}
.nl-me{position:relative;overflow:hidden;min-height:100%;background:radial-gradient(70% 60% at 50% 70%,#2a63d8 0%,transparent 70%),var(--brand)}
.nl-me::before{content:"";position:absolute;left:8%;top:-20%;height:140%;width:clamp(14px,1.6vw,26px);background:var(--accent);transform:rotate(16deg)}
.nl-me::after{content:"";position:absolute;left:calc(8% + clamp(30px,3.4vw,56px));top:-20%;height:140%;width:2px;background:var(--paper);opacity:.8;transform:rotate(16deg)}
.nl-me picture{position:absolute;z-index:1;left:50%;bottom:0;width:min(118%,calc(92svh * 1.05));translate:-50% 0}
.nl-me img{width:100%;height:auto;animation:nlrise 1.2s .1s var(--ease) both}
@keyframes nlrise{from{transform:translateY(8%) scale(1.06)}}
.nl-me-tag{position:absolute;z-index:2;left:clamp(16px,3vw,40px);bottom:clamp(16px,3vw,36px);display:flex;align-items:center;gap:12px;padding:8px 18px 8px 8px;border-radius:999px;background:rgba(0,14,43,.78);border:1px solid rgba(243,245,250,.12);font-size:.88rem;font-weight:700}
.nl-me-tag b{display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:var(--accent);color:var(--ink);font-size:.76rem;font-weight:900;font-stretch:115%}
.nl-me-tag small{display:block;color:#b8c2da;font-weight:500;font-size:.74rem}
.nl-join{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:clamp(100px,12vh,140px) clamp(20px,5vw,72px) clamp(40px,6vh,72px);background:radial-gradient(60% 50% at 50% 30%,rgba(10,58,156,.45) 0%,transparent 70%),linear-gradient(rgba(243,245,250,.035) 1px,transparent 1px) 0 0/56px 56px,linear-gradient(90deg,rgba(243,245,250,.035) 1px,transparent 1px) 0 0/56px 56px,var(--ink)}
.nl-watch{width:clamp(74px,8vw,110px);height:auto;margin-bottom:22px;color:var(--accent);filter:drop-shadow(0 18px 30px rgba(255,199,44,.18))}
.nl-watch .hand{transform-origin:50px 62px;transform-box:view-box;animation:nlhand 6s linear infinite}
@keyframes nlhand{to{transform:rotate(360deg)}}
.nl-eyebrow{display:inline-flex;align-items:center;gap:.6em;padding:7px 14px;border-radius:999px;border:1px solid currentColor;color:var(--accent);font-size:.68rem;font-weight:800;letter-spacing:.22em;text-transform:uppercase}
.nl-eyebrow::before{content:"";width:.55em;height:.55em;border-radius:50%;background:currentColor}
.nl-join h1{margin-top:18px;font-size:clamp(2.8rem,5.6vw,6rem);font-weight:900;font-stretch:112%;line-height:.9;letter-spacing:-.045em;text-transform:uppercase}
.nl-join h1 em{font-family:"Instrument Serif",Georgia,serif;font-style:italic;font-weight:400;font-stretch:100%;text-transform:none;letter-spacing:-.03em;color:var(--accent);padding-right:.04em}
.nl-sub{margin-top:18px;max-width:40ch;color:#c9d1e6;font-size:clamp(1.02rem,1.3vw,1.18rem);font-weight:500;line-height:1.5;text-wrap:balance}
.nl-join .nl-form{margin:26px auto 0;width:100%;text-align:left}
.nl-join .nl-btn{justify-self:stretch;justify-content:space-between}
.nl-join .nl-micro{text-align:center}
@media (max-width:900px){
  .nl-split{grid-template-columns:1fr;min-height:0}
  .nl-me{height:34svh;min-height:250px}
  .nl-me picture{width:min(100vw,calc((max(34svh,250px) - 62px) * 1.05))}
  .nl-me-tag{padding:6px 14px 6px 6px;font-size:.8rem}.nl-me-tag b{width:30px;height:30px}
  .nl-join{padding-top:28px}
  .nl-watch{display:none}
  .nl-join h1{margin-top:14px}
  .nl-sub{margin-top:12px}
  .nl-join .nl-form{margin-top:18px}
  .nl-join .nl-btn{margin-right:70px}
  .nl-me-tag{display:none}
}
@media (prefers-reduced-motion:reduce){.nl-me img,.nl-watch .hand{animation:none}}
.nl-micro{margin-top:14px;color:#b8c2da;font-size:.9rem;font-weight:600}
.nl-sec{padding:clamp(80px,11vw,150px) var(--pad)}
.nl-sec h2{font-size:clamp(2.4rem,6vw,5.4rem);font-weight:800;line-height:.94;letter-spacing:-.05em;text-wrap:balance;margin-bottom:clamp(36px,5vw,64px)}
.nl-sec h2 em{font-family:"Instrument Serif",Georgia,serif;font-style:italic;font-weight:400;color:var(--brand-2);letter-spacing:-.02em}
.nl-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:26px;list-style:none;padding:0;margin:0}
.nl-cards li{display:flex;flex-direction:column;gap:12px;min-height:260px;padding:26px 24px;border-radius:26px;background:#fff;box-shadow:0 0 0 6px rgba(0,33,94,.035),0 0 0 7px rgba(0,33,94,.09);transition:transform .5s var(--ease),box-shadow .5s var(--ease)}
.nl-cards li:hover{transform:translateY(-6px) rotate(-1deg);box-shadow:0 0 0 6px rgba(0,33,94,.05),0 0 0 7px rgba(0,33,94,.14),0 30px 50px -30px rgba(0,33,94,.45)}
.nl-cards .emo{font-size:2.2rem;line-height:1}
.nl-cards h3{margin-top:auto;font-size:1.35rem;font-weight:800;letter-spacing:-.02em;line-height:1.1}
.nl-cards p{color:#3a4766;font-size:.98rem}
@media (max-width:1000px){.nl-cards{grid-template-columns:1fr 1fr}}
@media (max-width:560px){.nl-cards{grid-template-columns:1fr}.nl-cards li{min-height:0}.nl-cards h3{margin-top:10px}}
.nl-who{background:var(--ink);color:var(--paper)}
.nl-who-grid{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:clamp(30px,6vw,90px);align-items:center}
.nl-who-photo{position:relative;border-radius:28px;overflow:hidden;background:radial-gradient(70% 60% at 50% 30%,#2a63d8 0%,var(--brand) 60%,var(--ink) 100%);aspect-ratio:4/4.6;box-shadow:0 0 0 6px rgba(243,245,250,.03),0 0 0 7px rgba(243,245,250,.1)}
.nl-who-photo img{position:absolute;left:8%;right:8%;bottom:0;width:84%;height:auto}
.nl-who h2{color:var(--paper)}
.nl-who h2 em{color:var(--accent)}
.nl-who p{max-width:46ch;color:#c9d1e6;font-size:clamp(1.1rem,1.6vw,1.35rem);line-height:1.5}
.nl-who p b{color:var(--paper)}
.nl-who .links{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}
@media (max-width:800px){.nl-who-grid{grid-template-columns:1fr}.nl-who-photo{max-width:380px}}
.nl-final{position:relative;overflow:hidden;background:var(--brand);color:var(--paper);text-align:left}
.nl-final h2{color:var(--paper)}
.nl-final h2 em{color:var(--accent)}
.nl-final-card{max-width:760px;padding:clamp(28px,5vw,56px);border-radius:32px;background:radial-gradient(80% 70% at 100% 0%,#0a3a9c 0%,transparent 70%),var(--ink);box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 0 0 6px rgba(243,245,250,.03),0 0 0 7px rgba(243,245,250,.1)}
.nl-final-card h2{margin-bottom:26px}
.legal{max-width:72ch}
.legal h2{font-size:clamp(1.4rem,2.6vw,2rem);font-weight:800;letter-spacing:-.025em;margin:2em 0 .6em}
.legal h2:first-child{margin-top:0}
.legal p,.legal li{color:#1d2a4d}
.legal ul{padding-left:1.2em}
.legal li+li{margin-top:.4em}
.legal dl{display:grid;grid-template-columns:minmax(150px,auto) 1fr;gap:10px 22px;margin:0;padding:22px;border-radius:20px;background:#fff;box-shadow:0 0 0 6px rgba(0,33,94,.035),0 0 0 7px rgba(0,33,94,.09)}
.legal dt{font-weight:800}
.legal dd{margin:0;color:#1d2a4d}
.legal a{color:var(--brand-2);text-decoration-thickness:2px;text-underline-offset:3px}
@media (max-width:600px){.legal dl{grid-template-columns:1fr;gap:2px}.legal dd{margin-bottom:12px}}
'''

FOOT = '''<footer class="foot"><span>© 2026 Oriol Huguet</span><span><a href="/newsletter/">Newsletter Punto Muerto</a> · <a href="/privacidad/">Privacidad</a></span><a href="/">Volver a la web ↑</a></footer>'''


def page_head(title, desc, url, og, ld, extra_css=""):
    h = head(title, desc, url, og, ld)
    fonts = ('<link rel="preload" href="/assets/fonts/instrument-serif-italic.woff2" as="font" type="font/woff2" crossorigin>\n'
             '<style>@font-face{font-family:"Instrument Serif";src:url(/assets/fonts/instrument-serif-italic.woff2) format("woff2");'
             'font-style:italic;font-weight:400;font-display:swap}' + extra_css + '</style>\n</head>')
    return h.replace("</head>", fonts, 1)


def og_newsletter():
    tmp = ROOT / "scripts" / ".archivo.ttf"
    f = TTFont(ROOT / "assets" / "fonts" / "archivo.woff2"); f.flavor = None; f.save(tmp)
    serif = ROOT / "scripts" / ".serif.ttf"
    g = TTFont(ROOT / "assets" / "fonts" / "instrument-serif-italic.woff2"); g.flavor = None; g.save(serif)

    def font(size, wght, wdth, path=tmp):
        ft = ImageFont.truetype(str(path), size)
        try:
            ft.set_variation_by_axes([wght, wdth])
        except Exception:
            pass
        return ft
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (0, 33, 94))
    d = ImageDraw.Draw(im)
    for r in range(380, 0, -6):  # resplandor azul
        a = int(10 + (380 - r) * 0.12)
        d.ellipse((900 - r, 120 - r, 900 + r, 120 + r), fill=(0, 33 + a // 3, 94 + a))
    d.polygon([(70, 0), (100, 0), (-60, H), (-90, H)], fill=(255, 199, 44))
    d.line([(130, 0), (-30, H)], fill=(243, 245, 250), width=3)
    d.rounded_rectangle((120, 70, 520, 112), radius=21, outline=(255, 199, 44), width=2)
    d.text((142, 79), "NEWSLETTER · CADA DOMINGO 17:00", font=font(20, 800, 110), fill=(255, 199, 44))
    d.text((112, 150), "PUNTO", font=font(150, 900, 118), fill=(243, 245, 250))
    d.text((130, 300), "Muerto", font=ImageFont.truetype(str(serif), 190), fill=(255, 199, 44))
    d.text((122, 515), "IA aplicada al deporte, en 5 minutos.", font=font(34, 700, 100), fill=(243, 245, 250))
    d.text((122, 560), "oriolhuguet.com/newsletter", font=font(24, 500, 100), fill=(140, 151, 179))
    im.save(ROOT / "assets" / "img" / "og-punto-muerto.jpg", quality=86, optimize=True)
    tmp.unlink(); serif.unlink()


def newsletter_page():
    url = f"{SITE}/newsletter/"
    ld = [person_ld(), {"@type": "WebPage", "@id": url, "url": url, "name": "Punto Muerto — Newsletter de IA y deporte",
                        "description": SUB, "inLanguage": "es", "author": {"@id": f"{SITE}/#oriol"},
                        "about": ["Inteligencia artificial", "Deporte", "Marketing deportivo"]}]
    cards = [("🏟️", "La jugada de la semana", "La noticia más importante de IA y deporte."),
             ("📡", "Radar IA", "Lo que se mueve en rendimiento, salud, scouting, marketing, ticketing y fans."),
             ("🛠️", "Herramienta de la semana", "Una IA útil para el deporte, explicada en corto."),
             ("⚡", "Momento de la semana", "La acción deportiva de la que todos hablan.")]
    cards_html = "".join(f'<li class="rv"><span class="emo" aria-hidden="true">{e}</span><h3>{t}</h3><p>{p}</p></li>' for e, t, p in cards)
    html = page_head("Punto Muerto — Newsletter de IA y deporte | Oriol Huguet", SUB, url,
                     f"{SITE}/assets/img/og-punto-muerto.jpg", ld, NL_CSS + PAGE_CSS).replace(
        "<style>", '<link rel="preload" as="image" type="image/avif" fetchpriority="high" imagesrcset="/assets/img/oriol-560.avif 560w, /assets/img/oriol-860.avif 860w, /assets/img/oriol-1240.avif 1240w" imagesizes="(max-width: 900px) 100vw, 50vw">\n<style>', 1) + f'''
<body>
{NAV.format(cur="").replace('<li><a href="/newsletter/">Newsletter</a></li>', '<li><a href="/newsletter/" aria-current="page">Newsletter</a></li>')}
<main id="main">
<section class="nl-split" aria-labelledby="nl-title">
  <div class="nl-me">
    <picture>
      <source type="image/avif" srcset="/assets/img/oriol-560.avif 560w, /assets/img/oriol-860.avif 860w, /assets/img/oriol-1240.avif 1240w" sizes="(max-width: 900px) 100vw, 50vw">
      <source type="image/webp" srcset="/assets/img/oriol-560.webp 560w, /assets/img/oriol-860.webp 860w, /assets/img/oriol-1240.webp 1240w" sizes="(max-width: 900px) 100vw, 50vw">
      <img src="/assets/img/oriol-860.webp" width="1240" height="1181" alt="Oriol Huguet, autor de la newsletter Punto Muerto" fetchpriority="high" decoding="async">
    </picture>
    <p class="nl-me-tag"><b>OH</b><span>Oriol Huguet<small>Autor de Punto Muerto</small></span></p>
  </div>
  <div class="nl-join">
    <svg class="nl-watch" viewBox="0 0 100 112" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" aria-hidden="true"><path d="M40 6h20M50 6v10M78 26l6-6"/><circle cx="50" cy="62" r="40"/><g class="hand"><path d="M50 62V36"/></g><circle cx="50" cy="62" r="4" fill="currentColor"/></svg>
    <span class="nl-eyebrow">Newsletter · Cada domingo 17:00</span>
    <h1 id="nl-title">Punto <em>Muerto</em></h1>
    <p class="nl-sub">{SUB}</p>
    {form_html("page", "top")}
    <p class="nl-micro">Gratis. Sin spam. Te das de baja con un clic.</p>
  </div>
</section>

<section class="nl-sec" aria-labelledby="nl-what">
  <h2 id="nl-what">Qué <em>recibirás</em></h2>
  <ul class="nl-cards">{cards_html}</ul>
</section>

<section class="nl-sec nl-who" aria-labelledby="nl-who-t">
  <div class="nl-who-grid">
    <div class="nl-who-photo rv"><picture><source type="image/avif" srcset="/assets/img/oriol-card.avif"><img src="/assets/img/oriol-card.webp" width="520" height="683" alt="Oriol Huguet" loading="lazy" decoding="async"></picture></div>
    <div>
      <h2 id="nl-who-t">Quién la <em>escribe</em></h2>
      <p>Soy <b>Oriol Huguet</b>. Trabajo en marketing y gestión deportiva y estoy construyendo un proyecto de IA para el deporte. Aquí comparto lo que aprendo cada semana.</p>
      <div class="links"><a class="btn btn--y" href="/">Conóceme</a><a class="btn btn--ink" href="https://www.linkedin.com/in/oriol-huguet-digital-retail/" target="_blank" rel="noopener" style="border-color:rgba(243,245,250,.2)">LinkedIn ↗</a></div>
    </div>
  </div>
</section>

<section class="nl-sec nl-final" aria-labelledby="nl-final-t">
  <div class="nl-final-card">
    <h2 id="nl-final-t">¿Te veo el <em>domingo?</em></h2>
    {form_html("page", "end")}
    <p class="nl-micro">Gratis. Sin spam. Te das de baja con un clic.</p>
  </div>
</section>
</main>
{FOOT}
{WA}
<script>(()=>{{const io=new IntersectionObserver(e=>e.forEach(x=>{{if(x.isIntersecting){{x.target.classList.add('in');io.unobserve(x.target)}}}}),{{rootMargin:'0px 0px -8% 0px'}});document.querySelectorAll('.rv').forEach(e=>io.observe(e))}})()</script>
{SCRIPTS}
</body>
</html>
'''
    (ROOT / "newsletter").mkdir(exist_ok=True)
    (ROOT / "newsletter" / "index.html").write_text(html)


def privacy_page():
    url = f"{SITE}/privacidad/"
    desc = "Política de privacidad de oriolhuguet.com y de la newsletter Punto Muerto: qué datos se recogen, para qué, con qué base legal y cómo ejercer tus derechos."
    ld = [person_ld(), {"@type": "WebPage", "@id": url, "url": url, "name": "Política de privacidad", "inLanguage": "es"}]
    html = page_head("Política de privacidad | Oriol Huguet", desc, url, f"{SITE}/assets/img/og-oriol-huguet.jpg", ld, PAGE_CSS) + f'''
<body>
{NAV.format(cur="")}
<main id="main">
<header class="bhero">
  <ol class="crumbs"><li><a href="/">Inicio</a></li><li>Privacidad</li></ol>
  <span class="label">Legal</span>
  <h1>Política de <em>privacidad</em></h1>
  <p class="lead">Qué datos recojo en esta web y en la newsletter Punto Muerto, para qué los uso y cómo puedes ejercer tus derechos.</p>
</header>
<section class="sec wrap">
  <div class="legal">
    <h2>Responsable</h2>
    <p>Oriol Huguet. Contacto: <a href="mailto:contact@oriolhuguet.com">contact@oriolhuguet.com</a>.</p>

    <h2 id="newsletter">Newsletter Punto Muerto</h2>
    <dl>
      <dt>Datos que recojo</dt><dd>Tu nombre y tu email.</dd>
      <dt>Finalidad</dt><dd>Enviarte cada semana la newsletter Punto Muerto.</dd>
      <dt>Base legal</dt><dd>Tu consentimiento, que das al marcar la casilla del formulario. Puedes retirarlo cuando quieras.</dd>
      <dt>Encargado del tratamiento</dt><dd>Kit (ConvertKit LLC, Estados Unidos), la plataforma con la que se envía la newsletter. Las transferencias internacionales de datos se amparan en las cláusulas contractuales tipo de la Comisión Europea.</dd>
      <dt>Conservación</dt><dd>Hasta que te des de baja.</dd>
      <dt>Baja</dt><dd>Con el enlace que aparece al final de cada email, o escribiéndome.</dd>
    </dl>

    <h2>Tus derechos</h2>
    <p>Puedes ejercer tus derechos de acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad (ARCO-POL) escribiendo a <a href="mailto:contact@oriolhuguet.com">contact@oriolhuguet.com</a>. Si consideras que no se han atendido correctamente, puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).</p>

    <h2>Preferencias guardadas en tu navegador</h2>
    <p>Esta web no usa cookies de seguimiento. Para no repetirte el aviso de la newsletter, guarda en el almacenamiento local de tu navegador si ya te has suscrito (<code>pm_subscribed</code>) y cuándo cerraste el aviso (<code>pm_popup_closed_at</code>). Estos datos no salen de tu dispositivo y puedes borrarlos desde la configuración del navegador.</p>

    <h2>Contacto por WhatsApp, email o teléfono</h2>
    <p>Si me escribes por WhatsApp, por email o me llamas, usaré tus datos solo para responderte.</p>

    <p style="margin-top:2.4em;color:#55617f;font-size:.9rem">Última actualización: 10 de noviembre de 2026.</p>
  </div>
</section>
</main>
{FOOT}
{WA}
{SCRIPTS}
</body>
</html>
'''
    (ROOT / "privacidad").mkdir(exist_ok=True)
    (ROOT / "privacidad" / "index.html").write_text(html)


def inject(path, marker, content):
    p = ROOT / path
    s = p.read_text()
    pat = re.compile(rf"(<!-- {marker}:start -->).*?(<!-- {marker}:end -->)", re.S)
    if not pat.search(s):
        raise SystemExit(f"Faltan los marcadores {marker} en {path}")
    p.write_text(pat.sub(lambda m: m.group(1) + content + m.group(2), s))


def main():
    og_newsletter()
    newsletter_page()
    privacy_page()
    inject("index.html", "nl-form", "\n" + form_html("home", "home") + "\n")
    for page in ("index.html", "cv/index.html"):
        inject(page, "nl-popup", "\n" + popup_template() + "\n" + SCRIPTS + "\n")
    print("newsletter, privacidad, portada y CV actualizados")


if __name__ == "__main__":
    main()
