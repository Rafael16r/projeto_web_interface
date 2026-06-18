import fs from 'fs';
import * as pdfjsLib from './node_modules/pdfjs-dist/build/pdf.mjs';
const input = 'C:/Users/PC/Desktop/interface/2025b-pw-pbl.pdf';
const data = new Uint8Array(fs.readFileSync(input));
const loadingTask = pdfjsLib.getDocument({ data, disableWorker: true });
const pdf = await loadingTask.promise;
const pages = [];
for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
  const page = await pdf.getPage(pageNum);
  const content = await page.getTextContent();
  const text = content.items.map(item => item.str).join(' ');
  pages.push(`--- PAGE ${pageNum} ---\n${text}`);
}
fs.mkdirSync('output', { recursive: true });
fs.writeFileSync('output/pbl_pdf_text.txt', pages.join('\n\n'), 'utf8');
console.log(`pages=${pdf.numPages}`);
