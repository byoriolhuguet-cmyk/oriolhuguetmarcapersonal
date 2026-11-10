"""Componente <NewsletterForm source="..."> de Punto Muerto (única fuente del marcado).

Lo usan build_newsletter.py (página /newsletter, portada, CV) y build_blog.py (blog).
El comportamiento está en /js/newsletter.js y los estilos en /css/newsletter.css.
"""

CONSENT = ('Acepto recibir Punto Muerto cada domingo y la '
           '<a href="/privacidad/">política de privacidad</a>. Puedo darme de baja cuando quiera.')


def form_html(source, uid):
    """Formulario de suscripción. `source`: page | popup | home. `uid`: sufijo único de los id."""
    return f'''<form class="nl-form" data-nl-form data-source="{source}" action="/api/subscribe" method="post" novalidate>
  <div class="nl-fields">
    <p class="nl-field"><label for="nl-name-{uid}">Nombre</label><input id="nl-name-{uid}" name="first_name" type="text" autocomplete="given-name" maxlength="60" required placeholder="Tu nombre"></p>
    <p class="nl-field"><label for="nl-email-{uid}">Email</label><input id="nl-email-{uid}" name="email" type="email" inputmode="email" autocomplete="email" maxlength="254" required placeholder="tu@email.com"></p>
  </div>
  <p class="nl-hp" aria-hidden="true"><label for="nl-web-{uid}">Deja este campo vacío</label><input id="nl-web-{uid}" name="website" type="text" tabindex="-1" autocomplete="off"></p>
  <label class="nl-consent" for="nl-ok-{uid}"><input id="nl-ok-{uid}" name="consent" type="checkbox" required><span>{CONSENT}</span></label>
  <button class="nl-btn" type="submit"><span class="nl-btn-t">Quiero recibirla</span><span class="nl-btn-i" aria-hidden="true">→</span></button>
  <p class="nl-msg" role="status" aria-live="polite"></p>
</form>'''


def popup_template():
    """Plantilla del pop-up; /js/newsletter.js la clona cuando toca mostrarla."""
    return f'''<template id="nl-popup-tpl"><div class="nl-pop" hidden>
  <div class="nl-pop-bg"></div>
  <div class="nl-pop-card" role="dialog" aria-modal="true" aria-labelledby="nl-pop-t" aria-describedby="nl-pop-d">
    <button class="nl-pop-x" type="button" aria-label="Cerrar">✕</button>
    <span class="nl-pop-tag">Punto Muerto</span>
    <h2 id="nl-pop-t">Cada domingo, la IA del deporte en <em>5 minutos</em></h2>
    <p class="nl-pop-sub" id="nl-pop-d">Únete a Punto Muerto. Gratis.</p>
    {form_html("popup", "pop")}
  </div>
</div></template>'''
