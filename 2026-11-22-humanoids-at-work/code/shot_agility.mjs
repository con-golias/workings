// Screenshot of the Ocean Tomo paragraph in Agility's Form S-4/A (SEC, 30 Sep 2026), the HTML file as filed, opened
// locally, with the two sentences outlined. Save the filing as data/raw/agility_s4a.htm, then:
//   PW=<path to node_modules/playwright> node code/shot_agility.mjs   ->  charts/shot-agility-s4.png
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || "playwright");
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SRC = pathToFileURL(path.join(root, "data", "raw", "agility_s4a.htm")).href;
const OUT = path.join(root, "charts", "shot-agility-s4.png");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 2 });
await page.goto(SRC, { waitUntil: "domcontentloaded", timeout: 180000 });
const box = await page.evaluate(() => {
  const needle = "The unadjusted opportunity pipeline estimates";
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n; while ((n = walker.nextNode())) { if (n.nodeValue.replace(/\s+/g, " ").includes(needle)) break; }
  if (!n) return null;
  let el = n.parentElement; while (el && el.getBoundingClientRect().height < 40) el = el.parentElement;
  const i = n.nodeValue.indexOf("The unadjusted"); const end = n.nodeValue.indexOf("deployed.", n.nodeValue.indexOf("Deployment Schedule estimates")) + "deployed.".length;
  if (i >= 0 && end > i) { const r = document.createRange(); r.setStart(n, i); r.setEnd(n, end); const m = document.createElement("mark");
    m.style.background = "rgba(111,132,150,0.22)"; m.style.outline = "2px solid #6F8496"; r.surroundContents(m); }
  el.scrollIntoView({ block: "center" });
  const b = el.getBoundingClientRect(); return { x: b.x, y: b.y, width: b.width, height: b.height };
});
if (!box) { console.log("not found"); process.exit(1); }
await page.screenshot({ path: OUT, clip: { x: Math.max(0, box.x - 12), y: Math.max(0, box.y - 12), width: Math.min(1100, box.width + 24), height: box.height + 24 } });
console.log("ok", box);
await browser.close();
