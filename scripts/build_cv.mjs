// Genera cv/oriol-huguet-cv.pdf a partir de /cv/ (página HTML imprimible).
// Requiere Playwright y la web servida en local: npx serve . -l 8818 && node scripts/build_cv.mjs
import { chromium } from 'playwright';
const url = process.env.CV_URL || 'http://localhost:8818/cv/';
const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage();
await page.goto(url, { waitUntil: 'networkidle' });
await page.emulateMedia({ media: 'print' });
await page.pdf({ path: new URL('../cv/oriol-huguet-cv.pdf', import.meta.url).pathname, format: 'A4', printBackground: true, margin: { top: '12mm', bottom: '12mm', left: '12mm', right: '12mm' } });
await browser.close();
console.log('cv/oriol-huguet-cv.pdf');
