#!/usr/bin/env python3
"""Genera el blog estático a partir de content/blog/*.md.

Crea /blog/index.html, /blog/<slug>/index.html, las imágenes Open Graph de
cada artículo y actualiza el bloque del blog en la portada, sitemap.xml y
llms.txt. Requiere: pip install markdown pillow fonttools brotli
Uso: python3 scripts/build_blog.py
"""
import html
import io
import json
import re
from datetime import date
from pathlib import Path

import markdown
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.oriolhuguet.com"
CONTENT = ROOT / "content" / "blog"
CSS = (ROOT / "scripts" / "blog.css").read_text()
MONTHS = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()
CAT = {"IA": "c-ia", "Marketing deportivo": "c-md", "Digital retail": "c-dr", "E-commerce": "c-ec", "Marca personal": "c-mp"}
WA_URL = "https://wa.me/34611416474?text=" + "Hola%20Oriol%2C%20he%20visto%20tu%20web%20y%20me%20gustar%C3%ADa%20hablar%20contigo"
WA_SVG = ('<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3.5A12.5 12.5 0 0 0 5.2 22.3L3.6 28.4l6.3-1.6A12.5 12.5 0 1 0 16 3.5z" '
          'fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/><path d="M11.9 9.6c.4-.4 1-.4 1.3.1l1.4 2c.3.4.2.9-.1 '
          '1.2l-.8.8c.6 1.4 1.8 2.6 3.2 3.2l.8-.8c.3-.3.8-.4 1.2-.1l2 1.4c.5.3.5.9.1 1.3l-1 1c-.8.8-2 1-3 .5-2.6-1.2-4.7-3.3-5.9-5.9-.5-1-.3-2.2.5-3z" '
          'fill="currentColor"/></svg>')
WA = f'<a class="wa" href="{WA_URL}" target="_blank" rel="noopener" aria-label="Escríbeme por WhatsApp">{WA_SVG}<span>¿Hablamos por WhatsApp?</span></a>'


def esc(s):
    return html.escape(s, quote=True)


def fdate(d):
    y, m, dd = map(int, d.split("-"))
    return f"{dd} de {MONTHS[m - 1]} de {y}"


def parse(path):
    raw = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    meta["body_md"] = m.group(2).strip()
    meta["read"] = int(meta.get("read") or 6)
    return meta


def render(meta):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                           extension_configs={"toc": {"slugify": lambda v, s: re.sub(r"[^a-z0-9]+", "-", v.lower()
                                                      .translate(str.maketrans("áéíóúüñ¿?¡!", "aeiouun    "))).strip("-")}})
    body = md.convert(meta["body_md"])
    toc = [(t["id"], t["name"]) for t in md.toc_tokens if t["level"] == 2 and t["id"] != "preguntas-frecuentes"]
    # preguntas frecuentes para JSON-LD
    faqs = []
    fq = meta["body_md"].split("## Preguntas frecuentes", 1)
    if len(fq) == 2:
        for q, a in re.findall(r"###\s*(.+?)\n+(.+?)(?=\n###|\Z)", fq[1], re.S):
            a = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", " ".join(a.split()))
            faqs.append({"@type": "Question", "name": q.strip(), "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"[*_`]", "", a)}})
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return body, toc, faqs, words


def og_image(meta, font_path):
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (0, 33, 94))
    d = ImageDraw.Draw(im)
    d.polygon([(70, 0), (100, 0), (-60, H), (-90, H)], fill=(255, 199, 44))
    d.line([(130, 0), (-30, H)], fill=(243, 245, 250), width=3)
    def font(size, wght, wdth):
        f = ImageFont.truetype(str(font_path), size)
        try:
            f.set_variation_by_axes([wght, wdth])
        except Exception:
            pass
        return f
    small = font(26, 800, 110)
    d.text((120, 70), meta["category"].upper() + "  ·  BLOG", font=small, fill=(255, 199, 44))
    size = 72
    title = meta["title"]
    while True:
        f = font(size, 900, 100)
        lines, line = [], ""
        for w in title.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=f) > 960 and line:
                lines.append(line); line = w
            else:
                line = t
        lines.append(line)
        if len(lines) <= 4 or size <= 48:
            break
        size -= 6
    y = 140
    for ln in lines:
        d.text((120, y), ln, font=f, fill=(243, 245, 250)); y += int(size * 1.08)
    d.ellipse((120, 512, 176, 568), fill=(255, 199, 44))
    d.text((134, 525), "OH", font=font(22, 900, 115), fill=(0, 14, 43))
    d.text((196, 520), "Oriol Huguet", font=font(30, 800, 100), fill=(243, 245, 250))
    d.text((196, 556), "IA · Marketing deportivo · Digital retail · E-commerce", font=font(20, 500, 100), fill=(140, 151, 179))
    out = ROOT / "assets" / "img" / "blog" / f"{meta['slug']}.jpg"
    im.save(out, quality=84, optimize=True)


def card(p, i, big=False):
    cls = "pcard rv" + (" pcard--big" if big else "")
    return (f'<a class="{cls}" href="/blog/{p["slug"]}/" data-cat="{esc(p["category"])}">'
            f'<div class="cover {CAT.get(p["category"], "c-ia")}" aria-hidden="true"><span>{esc(p["category"])}</span><b>{i:02d}</b></div>'
            f'<div class="pbody"><h3>{esc(p["title"])}</h3><p>{esc(p["excerpt"])}</p>'
            f'<small>{fdate(p["date"])} · {p["read"]} min</small></div></a>')


def head(title, desc, url, og, extra_ld, kind="website"):
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="Oriol Huguet">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#00215e">
<meta property="og:type" content="{kind}">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="Oriol Huguet">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/icon-180.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="text/plain" href="/llms.txt" title="Resumen para modelos de lenguaje">
<link rel="preload" href="/assets/fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": extra_ld}, ensure_ascii=False, separators=(",", ":"))}</script>
</head>'''


NAV = '''<a class="skip" href="#main">Saltar al contenido</a>
<div class="progress" aria-hidden="true"></div>
<header class="nav"><div class="island">
  <a class="brand" href="/"><b>OH</b><span>Oriol Huguet</span></a>
  <nav aria-label="Principal"><ul class="menu"><li><a href="/">Inicio</a></li><li><a href="/#servicios">Servicios</a></li><li><a href="/cv/">CV</a></li><li><a href="/blog/"{cur}>Blog</a></li></ul></nav>
  <a class="cta-pill" href="/#contacto">Hablemos</a>
</div></header>'''

CTA = f'''<section class="cta" aria-labelledby="cta-t">
  <h2 id="cta-t">¿Jugamos<br>juntos?</h2>
  <p>Si quieres aplicar la IA, el marketing deportivo o el e-commerce en tu club o tu marca, hablemos.</p>
  <div class="row"><a class="btn btn--ink" href="mailto:byoriolhuguet@gmail.com">byoriolhuguet@gmail.com</a><a class="btn btn--ink" href="{WA_URL}" target="_blank" rel="noopener">WhatsApp</a></div>
</section>
<footer class="foot"><span>© {date.today().year} Oriol Huguet</span><span>IA · Marketing deportivo · Digital retail · E-commerce</span><a href="/">Volver a la web ↑</a></footer>
{WA}'''

JS = '''<script>(()=>{const p=document.querySelector('.progress'),io=new IntersectionObserver(e=>e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{rootMargin:'0px 0px -8% 0px'});document.querySelectorAll('.rv').forEach(e=>io.observe(e));
const toc=[...document.querySelectorAll('.toc a')],hs=toc.map(a=>document.getElementById(a.hash.slice(1)));let t=0;addEventListener('scroll',()=>{if(t)return;t=requestAnimationFrame(()=>{t=0;const h=document.documentElement;p.style.transform=`scaleX(${scrollY/Math.max(1,h.scrollHeight-innerHeight)})`;let k=-1;hs.forEach((h,i)=>{if(h&&h.getBoundingClientRect().top<innerHeight*.3)k=i});toc.forEach((a,i)=>a.classList.toggle('on',i===k))})},{passive:true});
const f=document.querySelectorAll('.filters button');f.forEach(b=>b.addEventListener('click',()=>{f.forEach(x=>x.setAttribute('aria-pressed',x===b));const c=b.dataset.cat;document.querySelectorAll('.cards .pcard').forEach(a=>{a.hidden=c!=='*'&&a.dataset.cat!==c;a.classList.add('in')})}))})()</script>'''


def person_ld():
    return {"@type": "Person", "@id": f"{SITE}/#oriol", "name": "Oriol Huguet", "url": f"{SITE}/",
            "jobTitle": "Especialista en IA, Marketing Deportivo, Digital Retail y E-commerce",
            "sameAs": ["https://www.linkedin.com/in/oriol-huguet-digital-retail/"]}


def build():
    posts = sorted((parse(p) for p in CONTENT.glob("*.md")), key=lambda p: p["date"], reverse=True)
    tmp = ROOT / "scripts" / ".archivo.ttf"
    f = TTFont(ROOT / "assets" / "fonts" / "archivo.woff2"); f.flavor = None; f.save(tmp)
    sitemap = [f"{SITE}/", f"{SITE}/cv/", f"{SITE}/blog/"]
    for i, p in enumerate(posts):
        body, toc, faqs, words = render(p)
        og_image(p, tmp)
        url = f"{SITE}/blog/{p['slug']}/"
        sitemap.append(url)
        related = [q for q in posts if q is not p and q["category"] == p["category"]]
        related += [q for q in posts if q is not p and q not in related]
        ld = [person_ld(),
              {"@type": "BlogPosting", "@id": url + "#post", "headline": p["title"], "description": p["description"],
               "datePublished": p["date"], "dateModified": p["date"], "inLanguage": "es", "mainEntityOfPage": url,
               "author": {"@id": f"{SITE}/#oriol"}, "publisher": {"@id": f"{SITE}/#oriol"}, "keywords": p["keyword"],
               "articleSection": p["category"], "wordCount": words, "image": f"{SITE}/assets/img/blog/{p['slug']}.jpg"},
              {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{SITE}/"},
                  {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
                  {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]}]
        if faqs:
            ld.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": faqs})
        toc_html = "".join(f'<li><a href="#{a}">{esc(n)}</a></li>' for a, n in toc)
        page = head(f"{p['title']} | Oriol Huguet", p["description"], url, f"{SITE}/assets/img/blog/{p['slug']}.jpg", ld, "article") + f'''
<body>
{NAV.format(cur="")}
<main id="main">
<article>
<header class="bhero">
  <ol class="crumbs"><li><a href="/">Inicio</a></li><li><a href="/blog/">Blog</a></li><li>{esc(p["category"])}</li></ol>
  <span class="label">{esc(p["category"])}</span>
  <h1>{esc(p["title"])}</h1>
  <p class="lead">{esc(p["excerpt"])}</p>
  <div class="meta"><span class="who"><img src="/assets/img/oriol-avatar.webp" width="160" height="160" alt="Oriol Huguet"><span>Por <b>Oriol Huguet</b></span></span><time datetime="{p["date"]}">{fdate(p["date"])}</time><span>{p["read"]} min de lectura</span></div>
</header>
<div class="post wrap">
  <div class="prose">{body}</div>
  <aside class="side" aria-label="Índice y autor"><div class="side-in">
    <nav class="toc" aria-label="Índice del artículo"><p>En este artículo</p><ol>{toc_html}</ol></nav>
    <div class="author"><img src="/assets/img/oriol-avatar.webp" width="160" height="160" alt="" loading="lazy"><h2>Oriol Huguet</h2><p>Especialista en IA, marketing deportivo, digital retail y e-commerce. Profesor invitado de IA en Founderz y Director de Account Managers y Client Success en Spread It.</p><a class="btn btn--y" href="{WA_URL}" target="_blank" rel="noopener">Escríbeme</a></div>
  </div></aside>
</div>
</article>
<section class="sec wrap" aria-labelledby="rel-t" style="background:#fff">
  <h2 class="t" id="rel-t">Sigue<br><em>leyendo</em></h2>
  <div class="cards">{"".join(card(q, posts.index(q) + 1) for q in related[:3])}</div>
</section>
{CTA}
</main>
{JS}
</body>
</html>
'''
        d = ROOT / "blog" / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page)

    # índice del blog
    cats = list(dict.fromkeys(p["category"] for p in posts))
    filt = '<li><button type="button" data-cat="*" aria-pressed="true">Todos</button></li>' + "".join(
        f'<li><button type="button" data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button></li>' for c in cats)
    ld = [person_ld(), {"@type": "Blog", "@id": f"{SITE}/blog/#blog", "name": "Blog de Oriol Huguet", "url": f"{SITE}/blog/", "inLanguage": "es",
                        "author": {"@id": f"{SITE}/#oriol"},
                        "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/", "datePublished": p["date"]} for p in posts]}]
    desc = "Blog de Oriol Huguet sobre inteligencia artificial, marketing deportivo, digital retail y e-commerce: guías prácticas para clubes, deportistas y marcas."
    index = head("Blog de IA, marketing deportivo y e-commerce | Oriol Huguet", desc, f"{SITE}/blog/", f"{SITE}/assets/img/og-oriol-huguet.jpg", ld) + f'''
<body>
{NAV.format(cur=' aria-current="page"')}
<main id="main">
<header class="bhero">
  <ol class="crumbs"><li><a href="/">Inicio</a></li><li>Blog</li></ol>
  <span class="label">El blog</span>
  <h1>Ideas desde el <em>banquillo</em></h1>
  <p class="lead">Guías prácticas sobre inteligencia artificial, marketing deportivo, digital retail y e-commerce para clubes, deportistas y marcas. Lo que aprendo en el campo, en clase y en cada proyecto.</p>
</header>
<section class="sec wrap" aria-labelledby="arts-t">
  <h2 class="sr" id="arts-t">Todos los artículos</h2>
  <ul class="filters" aria-label="Filtrar por tema">{filt}</ul>
  <div class="cards">{card(posts[0], 1, True)}{"".join(card(p, i + 2) for i, p in enumerate(posts[1:]))}</div>
</section>
{CTA}
</main>
{JS}
</body>
</html>
'''
    (ROOT / "blog" / "index.html").write_text(index)
    tmp.unlink()

    # portada: últimos artículos
    home = ROOT / "index.html"
    h = home.read_text()
    teaser = "".join(card(p, i + 1) for i, p in enumerate(posts[:3]))
    h = re.sub(r"(<!-- blog:start -->).*?(<!-- blog:end -->)", lambda m: m.group(1) + teaser + m.group(2), h, flags=re.S)
    home.write_text(h)

    # sitemap
    today = date.today().isoformat()
    urls = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in sitemap)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')

    # llms.txt
    llms = ROOT / "llms.txt"
    t = llms.read_text().split("\n## Blog\n")[0].rstrip() + "\n\n## Blog\n" + "".join(
        f"- [{p['title']}]({SITE}/blog/{p['slug']}/): {p['excerpt']}\n" for p in posts)
    llms.write_text(t)
    print(f"{len(posts)} artículos generados")


if __name__ == "__main__":
    build()
