# oriolhuguet.com — web de marca personal

Web estática de una sola página: HTML con el CSS crítico incluido, un JS de 5 KB diferido y ninguna dependencia ni petición a terceros.

## Publicar
- **Vercel**: importa este repositorio tal cual (sin framework ni comando de build). `vercel.json` ya incluye las cabeceras de caché y seguridad.
- Dominio: añade `www.oriolhuguet.com` en Vercel → Settings → Domains.
- También vale cualquier hosting estático: sube el contenido de esta carpeta.
- Vista local: `python3 -m http.server` y abrir http://localhost:8000

## Añadir logos
1. Guarda el logo en `assets/img/logos/` en WebP, con fondo transparente y unos 200 px de alto.
2. En `index.html`, en el muro «Escudos que he defendido», cambia la ficha de texto (`club--txt`) por
   `<figure class="club"><img src="assets/img/logos/NOMBRE.webp" width="…" height="200" alt="" loading="lazy" decoding="async"><figcaption>Nombre</figcaption></figure>`.
3. En la trayectoria, pon la ruta en `data-logo="…"` del puesto y añade `<img class="job-logo" …>` (es la versión móvil, copia la de Spread It).

## SEO y agentes
- Datos estructurados `Person` + `ProfilePage` (experiencia, formación, credenciales, idiomas, LinkedIn).
- `llms.txt` con el perfil en texto plano para asistentes de IA, `sitemap.xml`, `robots.txt` e imagen Open Graph.
- Si cambias el CV, actualiza también `llms.txt` y el JSON-LD.
