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

## Blog
- Artículos en `content/blog/*.md` (front matter: title, slug, description, keyword, category, date, read, excerpt).
- Para publicar uno nuevo: añade el `.md` y ejecuta `pip install markdown pillow fonttools brotli && python3 scripts/build_blog.py`. Genera `/blog/`, la página del artículo, su imagen para redes, los últimos artículos de la portada, `sitemap.xml` y la lista de `llms.txt`.
- El blog no está en el menú de la portada: se llega desde «Leer el blog», el bloque «Últimos artículos» y el pie.

## WhatsApp
- Botón flotante en todas las páginas hacia wa.me/34611416474 con un mensaje inicial. Para cambiar el número, edita `WA_URL` en `scripts/build_blog.py` y el enlace `.wa` de `index.html`.

## Animaciones
- **Carga** (unos 4 s, solo la primera visita de cada sesión): esfera de cronómetro que se dibuja mientras pasan pictogramas de atletismo, baloncesto, tenis, ciclismo, natación y fútbol; palabras que rotan hasta «Oriol Huguet», cronómetro 00:02.80, barra de progreso y salida en apertura circular azul y amarilla. Todo en CSS.
- **Portada**: al entrar solo se ve el nombre; al hacer scroll el escenario se queda fijo y la foto sube desde abajo. «Rayos X»: al pasar el ratón (o el dedo en móvil) por la portada, un foco revela la versión azul y amarilla de la foto; esa imagen se pide con la primera interacción.
- **Scroll**: scroll suave con inercia (ratón), titulares palabra a palabra, etiquetas que se descifran, servicios en horizontal fijados (escritorio), cinta que cambia de sentido con el scroll, firma gigante en el pie, listas escalonadas, barra de progreso y botones magnéticos.
- Todo se desactiva con «reducir movimiento» del sistema; en móvil se quitan los efectos de ratón y el scroll horizontal.

## SEO y agentes
- Posicionado como especialista en IA, marketing deportivo, digital retail y e-commerce (title, description, H1, JSON-LD y FAQ).
- Datos estructurados `Person` + `ProfilePage` + `FAQPage` (experiencia, formación, credenciales, idiomas, LinkedIn).
- `llms.txt` con el perfil en texto plano para asistentes de IA, `sitemap.xml`, `robots.txt` e imagen Open Graph.
- Si cambias el CV, actualiza también `llms.txt` y el JSON-LD.
