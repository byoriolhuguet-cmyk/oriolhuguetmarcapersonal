"""Reservas con Calendly: configuración y componentes (única fuente).

Para cambiar el enlace de Calendly solo hay que tocar CALENDLY_URL (y, si
creas un evento distinto para cada tipo, el campo `url` de cada uno) y
volver a ejecutar: python3 scripts/build_reservar.py
"""
from urllib.parse import quote, urlencode

# Enlace del evento de Calendly (lo copias en Calendly → tu evento → «Copiar enlace»).
CALENDLY_URL = "https://calendly.com/byoriolhuguet/30min"

# Los tres tipos de sesión. Con un solo evento en Calendly (plan gratuito), cada
# botón rellena la primera pregunta del formulario («¿Qué tipo de sesión
# quieres?») con su valor (`a1`). Si tienes un evento por tipo, pon su enlace en `url`.
TYPES = [
    {"key": "consultoria", "emoji": "💡", "title": "Consultoría",
     "who": "Clubes, marcas y agencias",
     "desc": "IA aplicada, marketing deportivo, digital retail o e-commerce. Revisamos tu caso y te llevas los siguientes pasos.",
     "url": None},
    {"key": "mentoria", "emoji": "🧭", "title": "Mentoría",
     "who": "Estudiantes y perfiles que empiezan",
     "desc": "Carrera en marketing deportivo o IA, formación, portfolio y marca personal. Te cuento lo que me habría ahorrado tiempo.",
     "url": None},
    {"key": "empleo", "emoji": "🤝", "title": "Reunión para un puesto",
     "who": "Empresas y reclutadores",
     "desc": "¿Tienes un puesto en el que encajo? Hablamos del rol, del equipo y de cómo puedo aportar desde el primer día.",
     "url": None},
]
DURATION = "30 min"
ARROW = '<span class="bk-arrow" aria-hidden="true">→</span>'


def link(t, placement):
    """Enlace a Calendly del tipo `t`, con el tipo rellenado y UTM para saber desde dónde reservan."""
    base = t["url"] or CALENDLY_URL
    params = {"utm_source": "oriolhuguet.com", "utm_medium": "web", "utm_campaign": placement, "utm_content": t["key"]}
    if not t["url"]:
        params = {"a1": t["title"], **params}
    return f"{base}?{urlencode(params, quote_via=quote)}"


def cards(placement, compact=False):
    """Zona de reserva: una tarjeta por tipo de sesión, cada una lleva a Calendly."""
    cls = "bk-cards bk-cards--compact" if compact else "bk-cards"
    items = "".join(
        f'''<li><a class="bk-card" href="{link(t, placement)}" data-book="{t['key']}">
  <span class="bk-top"><span class="bk-emo" aria-hidden="true">{t['emoji']}</span><span class="bk-meta">{DURATION} · Gratis</span></span>
  <span class="bk-title">{t['title']}</span>
  <span class="bk-who">{t['who']}</span>
  {'' if compact else f'<span class="bk-desc">{t["desc"]}</span>'}
  <span class="bk-cta">Reservar hora {ARROW}</span>
</a></li>''' for t in TYPES)
    return f'<ul class="{cls}">{items}</ul>'


CSS = '''
.bk-cards{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.bk-card{position:relative;display:flex;flex-direction:column;gap:8px;height:100%;padding:22px 22px 20px;border-radius:24px;text-decoration:none;color:#f3f5fa;background:linear-gradient(180deg,#0a2160,#06194a);box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 0 0 6px rgba(243,245,250,.03),0 0 0 7px rgba(243,245,250,.1);overflow:hidden;isolation:isolate;transition:transform .5s cubic-bezier(.2,.8,.2,1),color .4s}
.bk-card::before{content:"";position:absolute;inset:0;z-index:-1;background:#ffc72c;clip-path:circle(0 at 100% 0);transition:clip-path .7s cubic-bezier(.2,.8,.2,1)}
.bk-card:hover,.bk-card:focus-visible{color:#000e2b;transform:translateY(-6px)}
.bk-card:hover::before,.bk-card:focus-visible::before{clip-path:circle(150% at 100% 0)}
.bk-card:focus-visible{outline:3px solid #f3f5fa;outline-offset:3px}
.bk-top{display:flex;justify-content:space-between;align-items:center;gap:10px}
.bk-emo{display:grid;place-items:center;width:44px;height:44px;border-radius:14px;background:rgba(243,245,250,.08);font-size:1.35rem}
.bk-meta{font-size:.66rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:#ffc72c;transition:color .4s}
.bk-card:hover .bk-meta,.bk-card:focus-visible .bk-meta{color:#000e2b}
.bk-title{margin-top:10px;font-size:1.45rem;font-weight:800;letter-spacing:-.02em;line-height:1.05}
.bk-who{font-size:.86rem;font-weight:700;opacity:.75}
.bk-desc{font-size:.95rem;line-height:1.45;opacity:.85}
.bk-cta{margin-top:auto;padding-top:14px;display:flex;justify-content:space-between;align-items:center;font-weight:800}
.bk-arrow{display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:#ffc72c;color:#000e2b;transition:transform .5s cubic-bezier(.32,.72,0,1),background .4s}
.bk-card:hover .bk-arrow,.bk-card:focus-visible .bk-arrow{background:#000e2b;color:#ffc72c;transform:translate(3px,-2px)}
.bk-cards--compact .bk-card{padding:18px 18px 16px}
.bk-cards--compact .bk-title{font-size:1.2rem;margin-top:6px}
@media (max-width:860px){.bk-cards{grid-template-columns:1fr}.bk-card{min-height:0}}
@media (prefers-reduced-motion:reduce){.bk-card,.bk-card::before,.bk-arrow{transition:none}}
'''
