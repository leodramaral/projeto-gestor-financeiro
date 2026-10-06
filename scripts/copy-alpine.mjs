// Copia o Alpine.js e o Chart.js do node_modules para static/dist, para servi-los localmente (sem CDN).
import { copyFileSync, mkdirSync } from "node:fs";

mkdirSync("static/dist/js", { recursive: true });
copyFileSync("node_modules/alpinejs/dist/cdn.min.js", "static/dist/js/alpine.min.js");
copyFileSync("node_modules/chart.js/dist/chart.umd.min.js", "static/dist/js/chart.umd.min.js");
