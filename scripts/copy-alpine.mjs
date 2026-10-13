// Copies Alpine.js, Chart.js, flatpickr (and its pt locale) and the Outfit font from node_modules to static/dist, so they are
// served locally (no CDN, no network at build time). The font is only the `latin` subset, which
// covers the accents of Brazilian Portuguese; frontend/style.css points its @font-face at it.
import { copyFileSync, mkdirSync } from "node:fs";

mkdirSync("static/dist/js", { recursive: true });
copyFileSync("node_modules/alpinejs/dist/cdn.min.js", "static/dist/js/alpine.min.js");
copyFileSync("node_modules/chart.js/dist/chart.umd.min.js", "static/dist/js/chart.umd.min.js");

copyFileSync("node_modules/flatpickr/dist/flatpickr.min.js", "static/dist/js/flatpickr.min.js");
copyFileSync("node_modules/flatpickr/dist/l10n/pt.js", "static/dist/js/flatpickr-pt.js");

mkdirSync("static/dist/fonts", { recursive: true });
copyFileSync(
  "node_modules/@fontsource-variable/outfit/files/outfit-latin-wght-normal.woff2",
  "static/dist/fonts/outfit-latin-wght-normal.woff2",
);
