// Copia o Alpine.js do node_modules para static/dist, para servi-lo localmente (sem CDN).
import { copyFileSync, mkdirSync } from "node:fs";

mkdirSync("static/dist/js", { recursive: true });
copyFileSync("node_modules/alpinejs/dist/cdn.min.js", "static/dist/js/alpine.min.js");
