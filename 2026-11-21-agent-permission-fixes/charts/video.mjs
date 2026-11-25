// Renders video.html frame by frame (30 fps, 14 s) into FRAMES, then: ffmpeg -framerate 30 -i FRAMES/%04d.png -c:v libx264 -crf 16 -pix_fmt yuv420p video.mp4
//   BASE=http://127.0.0.1:8791/charts FRAMES=<scratch dir> PW=<playwright> node charts/video.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || "playwright");
const out = process.env.FRAMES; fs.mkdirSync(out, { recursive: true });
const FPS = 30, SECONDS = 14;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
await page.goto(`${process.env.BASE}/video.html`);
await page.evaluate(() => Promise.all(["400", "500", "600", "700"].map((w) => document.fonts.load(`${w} 16px "Inter Tight"`))));
await page.evaluate(() => window.ready);
for (let f = 0; f < FPS * SECONDS; f++) {
  await page.evaluate((t) => window.draw(t), f / FPS);
  await page.screenshot({ path: path.join(out, `${String(f).padStart(4, "0")}.png`) });
}
await browser.close();
console.log(FPS * SECONDS, "frames");
