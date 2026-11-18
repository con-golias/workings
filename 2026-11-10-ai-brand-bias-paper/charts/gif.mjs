import { createRequire } from "node:module"; import path from "node:path";
const { chromium } = createRequire(import.meta.url)(process.env.PW);
const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1200, height: 675 }, deviceScaleFactor: 1 });
await pg.goto(`${process.env.BASE}/${process.env.PAGE}`);
await pg.evaluate(() => Promise.all(["400","600","700"].map(w => document.fonts.load(`${w} 20px "Inter Tight"`))));
await pg.evaluate(() => window.ready);
const FPS = 15, SEC = +process.env.SEC;
for (let f = 0; f < FPS * SEC; f++) { await pg.evaluate((t) => window.draw(t), f / FPS); await pg.screenshot({ path: path.join(process.env.OUT, `${String(f).padStart(4,"0")}.png`) }); }
await b.close(); console.log(FPS * SEC, "frames");
