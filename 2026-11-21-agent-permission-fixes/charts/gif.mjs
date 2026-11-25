// Renders gif.html to frames (15 fps, 8 s) and assembles a looping GIF with Pillow.
//   BASE=http://127.0.0.1:8797/charts FRAMES=<scratch dir> PW=<playwright> node charts/gif.mjs
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || "playwright");
const FPS = 15, SECONDS = 8;
const browser = await chromium.launch();
for (const g of ["changelog"]) {
  const dir = path.join(process.env.FRAMES, g); fs.mkdirSync(dir, { recursive: true });
  const page = await browser.newPage({ viewport: { width: 1200, height: 675 }, deviceScaleFactor: 1 });
  await page.goto(`${process.env.BASE}/gif.html?g=${g}`);
  await page.evaluate(() => Promise.all(["400", "600", "700"].map((w) => document.fonts.load(`${w} 16px "Inter Tight"`))));
  await page.evaluate(() => window.ready);
  for (let f = 0; f < FPS * SECONDS; f++) {
    await page.evaluate((t) => window.draw(t), f / FPS);
    await page.screenshot({ path: path.join(dir, `${String(f).padStart(4, "0")}.png`) });
  }
  await page.close();
  const py = `import glob,sys
from PIL import Image
fs=sorted(glob.glob(sys.argv[1]+'/*.png'));im=[Image.open(f).convert('RGB').quantize(64) for f in fs]
d=[1000//${FPS}]*len(im);d[-1]=2500
im[0].save(sys.argv[2],save_all=True,append_images=im[1:],duration=d,loop=0,optimize=True)`;
  execFileSync("python", ["-c", py, dir, path.join(here, `gif-${g}.gif`)]);
  console.log(`gif-${g}.gif`);
}
await browser.close();
