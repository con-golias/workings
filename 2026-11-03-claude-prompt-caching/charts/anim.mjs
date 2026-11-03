// Renders anim.html to PNG frames (30 per second, 0–13 s, 2× pixels) in charts/frames/anim/; then ffmpeg makes the MP4
// and anim_gif.py the GIF.   BASE=http://127.0.0.1:8771/charts PW=<path to node_modules/playwright> [ONLY=3,13] node charts/anim.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || "playwright");
const out = path.join(here, "frames", "anim");
fs.mkdirSync(out, { recursive: true });
const FPS = 30;
const times = process.env.ONLY ? process.env.ONLY.split(",").map(Number) : Array.from({ length: 13 * FPS }, (_, i) => i / FPS);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 720 }, deviceScaleFactor: 2 });
for (const t of times) {
  await page.goto(`${process.env.BASE}/anim.html?t=${t}`);
  await page.waitForFunction(() => window.done === true);
  await page.screenshot({ path: path.join(out, `${String(Math.round(t * FPS)).padStart(4, "0")}.png`) });
}
await browser.close();
console.log(times.length, "frames");
