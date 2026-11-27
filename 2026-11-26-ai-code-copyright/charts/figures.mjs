// Renders figures.html to PNGs at 2x: the figures (2400x1440) and the 5:2 cover (3000x1200).
//   python -m http.server <port>   (from the article folder), then
//   BASE=http://127.0.0.1:<port>/charts PW=<path to playwright> node charts/figures.mjs [names...]
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || "playwright");
const NAMES = { 1: "fig1-timeline", 2: "fig2-rate", 3: "fig3-who", 4: "fig4-wording", 5: "fig5-office", cover: "cover" };
const only = process.argv.slice(2);
const browser = await chromium.launch();
for (const [n, name] of Object.entries(NAMES)) {
  if (only.length && !only.includes(n)) continue;
  const page = await browser.newPage({ viewport: n === "cover" ? { width: 1500, height: 600 } : { width: 1200, height: 720 }, deviceScaleFactor: 2 });
  page.on("pageerror", (e) => console.log("ERR", name, e.message));
  await page.goto(`${process.env.BASE}/figures.html?fig=${n}`);
  await page.evaluate(() => window.ready);
  await page.evaluate(() => Promise.all(["400", "600", "700"].map((w) => document.fonts.load(`${w} 16px "Inter Tight"`))));
  await page.evaluate(() => window.ready);
  await page.screenshot({ path: path.join(here, `${name}.png`) });
  await page.close(); console.log(name);
}
await browser.close();
