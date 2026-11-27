/**
 * lang-switch.js — l'unico pezzo condiviso del bilinguismo.
 *
 * Le pagine sono **due file generati** (uno per lingua) dallo stesso dato: il
 * testo non è tradotto a runtime, è scritto due volte al build. Qui c'è solo il
 * link che porta all'altra lingua, con `hreflang` e `lang` corretti — che è ciò
 * che i motori di ricerca usano per capire che le due pagine sono la stessa.
 *
 * `pathIt` / `pathEn` sono i path pubblici, così il link resta corretto anche
 * se un giorno cambia la struttura delle cartelle.
 */
export function langSwitch({ lang, pathIt, pathEn }) {
  const to = lang === "it" ? pathEn : pathIt;
  const label = lang === "it" ? "English" : "Italiano";
  const target = lang === "it" ? "en" : "it";
  return `<a class="lang-switch" href="${to}" hreflang="${target}" lang="${target}">${label}</a>`;
}
