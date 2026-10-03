// Render the HTML produced by build_pdf.py to an A4 PDF with page numbers.
// Usage: node tools/render_pdf.mjs INPUT_HTML OUTPUT_PDF
import { createRequire } from 'node:module';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require('playwright');
} catch {
  playwright = require('/opt/node22/lib/node_modules/playwright');
}

const [input, output] = process.argv.slice(2);
const browser = await playwright.chromium.launch();
const page = await browser.newPage();
await page.goto(pathToFileURL(path.resolve(input)).href, { waitUntil: 'load' });
await page.waitForFunction(() => document.body.dataset.ready, null, { timeout: 60000 });
const state = await page.evaluate(() => document.body.dataset.ready);
if (state !== '1') console.warn('Mermaid rendering reported an error; diagrams may show as code.');
await page.evaluate(() => document.fonts.ready);
await page.pdf({
  path: output,
  format: 'A4',
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: '<div></div>',
  footerTemplate:
    '<div style="width:100%;font-size:8px;color:#6b7280;text-align:center;">หน้า <span class="pageNumber"></span> จาก <span class="totalPages"></span></div>',
  margin: { top: '16mm', bottom: '18mm', left: '14mm', right: '14mm' },
});
await browser.close();
console.log(`wrote ${output}`);
