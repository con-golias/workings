// usage.html -> usage-log.png (2×).  BASE=http://127.0.0.1:8771/charts PW=<path to playwright> node charts/usage.mjs
import { createRequire } from "node:module"; import path from "node:path"; import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url)); const { chromium } = createRequire(import.meta.url)(process.env.PW || "playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 720 }, deviceScaleFactor: 2 });
await p.goto(`${process.env.BASE}/usage.html`); await p.waitForFunction(() => window.done === true);
await p.evaluate(() => document.fonts.load('400 18px "JetBrains Mono"')); await p.screenshot({ path: path.join(here, "usage-log.png") }); await b.close();
