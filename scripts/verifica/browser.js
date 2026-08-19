// Helper condiviso per gli script di verifica Playwright.
// - Risolve CHROME_PATH (env o cache locale Playwright)
// - BASE_URL configurabile (env, default preview locale)
// Uso:
//   import { launchPage } from "./browser.js";
//   const page = await launchPage();
import { chromium } from "playwright";

const DEFAULT_CHROME = "/home/gabry/.cache/ms-playwright/chromium-1178/chrome-linux/chrome";

export const BASE_URL = process.env.BASE_URL || "http://localhost:8788";

export function chromePath() {
  return process.env.CHROME_PATH || DEFAULT_CHROME;
}

export async function launchPage(options = {}) {
  const browser = await chromium.launch({ executablePath: chromePath() });
  const page = await browser.newPage(options);
  return { browser, page };
}

export async function goto(page, path = "/dataset/anzianita", timeout = 60000) {
  await page.goto(BASE_URL + path, { waitUntil: "networkidle", timeout });
  await page.waitForTimeout(2500);
}
