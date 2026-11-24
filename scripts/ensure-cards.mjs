/**
 * ensure-cards.mjs — genera src/data/cards.json se assente.
 *
 * `cards.json` è un artefatto (gitignored). Il deploy lo produce con
 * `npm run cards`; questo hook rende ermetici `npm run build`, `npm run dev`
 * e `npm run preview` da un clone pulito, senza aggiungere query GCS a ogni
 * build quando il file esiste già.
 */
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const CARDS = resolve(ROOT, "src/data/cards.json");

if (!existsSync(CARDS)) {
  const [command, ...args] = (process.env.PYTHON3 || "python3").split(/\s+/);
  console.log("cards.json assente: genero le schede…");
  execFileSync(command, [...args, "scripts/build_cards.py"], {
    cwd: ROOT,
    stdio: "inherit",
  });
}
