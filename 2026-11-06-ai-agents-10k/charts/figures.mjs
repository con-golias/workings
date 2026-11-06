// Renders figures.html to static PNGs at 2×: the figures (2400×1440) and the 5:2 cover (3000×1200).
//   BASE=http://127.0.0.1:8771/charts PW=<path to node_modules/playwright> node charts/figures.mjs
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || "playwright");
const NAMES = { 1: "fig1-share", 2: "fig2-warnings", 3: "fig3-reused", 4: "fig4-sellers", cover: "cover" };
const browser = await chromium.launch();
for (const [n, name] of Object.entries(NAMES)) {
  const page = await browser.newPage({ viewport: n === "cover" ? { width: 1500, height: 600 } : { width: 1200, height: 720 }, deviceScaleFactor: 2 });
  await page.goto(`${process.env.BASE}/figures.html?fig=${n}`);
  await page.evaluate(() => window.ready);
  // Webfonts load only when used; ask for every face, then redraw.
  await page.evaluate(() => Promise.all(["400", "600", "700"].map((w) => document.fonts.load(`${w} 16px "Inter Tight"`))));
  await page.evaluate(() => window.ready);
  await page.screenshot({ path: path.join(here, `${name}.png`) });
  await page.close();
  console.log(name);
}
await browser.close();
