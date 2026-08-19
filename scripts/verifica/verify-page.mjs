// Verifica reale della pagina dataset con Playwright (browser headless).
// Carica la pagina, cattura errori console e riporta cosa è renderizzato.
//
// Uso (serve la preview o un server):
//   npx observable preview --port 8788
//   node scripts/verifica/verify-page.mjs [/dataset/slug]
/* global document */
import { chromium } from "playwright";
import { BASE_URL, chromePath } from "./browser.js";

const path = process.argv[2] || "/dataset/anzianita";
const url = BASE_URL + path;

const browser = await chromium.launch({ executablePath: chromePath() });
const page = await browser.newPage();

const consoleErrors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(`[console.error] ${msg.text()}`);
});
page.on("pageerror", (err) => consoleErrors.push(`[pageerror] ${err.message}`));
page.on("response", (resp) => {
  if (resp.status() >= 400) consoleErrors.push(`[http ${resp.status()}] ${resp.url()}`);
});

await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
await page.waitForTimeout(3000);

const result = await page.evaluate(() => {
  const sections = [...document.querySelectorAll("[data-section]")].map((s) => s.dataset.section);
  return {
    sections,
    svgCount: document.querySelectorAll("svg").length,
    tableCount: document.querySelectorAll("table").length,
    selectCount: document.querySelectorAll("select").length,
    bodyText: document.body.innerText.slice(0, 400),
  };
});

console.log("URL:", url);
console.log("=== SEZIONI renderizzate:", result.sections);
console.log("=== SVG:", result.svgCount, "| TABLE:", result.tableCount, "| SELECT:", result.selectCount);
console.log("=== BODY (primi 400 char):");
console.log(result.bodyText);

if (consoleErrors.length) {
  console.log("=== ERRORI CONSOLE ===");
  for (const e of consoleErrors) console.log(e);
} else {
  console.log("=== NESSUN ERRORE CONSOLE ===");
}

await browser.close();
