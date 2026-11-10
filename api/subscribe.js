// Suscripción a la newsletter Punto Muerto en Kit (API v4).
// Variables de entorno (en Vercel, nunca en el repo): KIT_API_KEY, KIT_FORM_PAGE, KIT_FORM_POPUP.
const KIT = 'https://api.kit.com/v4';
const SITE = 'https://www.oriolhuguet.com';
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const GENERIC = 'Algo ha fallado, inténtalo de nuevo';

const readBody = req => {
  if (req.body && typeof req.body === 'object') return req.body;
  try { return JSON.parse(req.body || '{}'); } catch { return {}; }
};

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Método no permitido' });
  }

  const { first_name = '', email = '', source = 'page', website = '' } = readBody(req);

  // Honeypot: los bots rellenan el campo oculto. Respondemos como si nada.
  if (String(website).trim()) return res.status(200).json({ ok: true });

  const name = String(first_name).trim();
  const mail = String(email).trim().toLowerCase();
  if (!name || name.length > 60 || mail.length > 254 || !EMAIL.test(mail)) {
    return res.status(400).json({ error: 'Revisa tu nombre y email' });
  }

  const { KIT_API_KEY, KIT_FORM_PAGE, KIT_FORM_POPUP } = process.env;
  const formId = source === 'popup' ? KIT_FORM_POPUP : KIT_FORM_PAGE;
  if (!KIT_API_KEY || !formId) {
    console.error('newsletter: faltan variables de entorno de Kit');
    return res.status(500).json({ error: GENERIC });
  }

  const headers = { 'X-Kit-Api-Key': KIT_API_KEY, 'Content-Type': 'application/json', Accept: 'application/json' };
  const path = source === 'page' ? '/newsletter/' : '/';

  try {
    // 1. Crear o actualizar el suscriptor (si ya existe, Kit lo devuelve sin error).
    const r1 = await fetch(`${KIT}/subscribers`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ email_address: mail, first_name: name.slice(0, 60), state: 'active' }),
    });
    if (!r1.ok && r1.status !== 422) throw new Error(`subscribers ${r1.status}`);

    // 2. Añadirlo al formulario que corresponde a su origen.
    const r2 = await fetch(`${KIT}/forms/${encodeURIComponent(formId)}/subscribers`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ email_address: mail, referrer: SITE + path }),
    });
    if (!r2.ok && r2.status !== 422) throw new Error(`forms ${r2.status}`);

    return res.status(200).json({ ok: true });
  } catch (e) {
    // Solo el código de estado: nunca la clave ni la respuesta de Kit.
    console.error('newsletter:', e.message);
    return res.status(500).json({ error: GENERIC });
  }
}
