# Assembles charts/frames/anim/*.png (30 per second, every third frame used) into charts/anim-prompt-caching.gif, looping.
#   python3 charts/anim_gif.py
import os
import sys
from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
d = os.path.join(here, "frames", "anim")
files = sorted(f for f in os.listdir(d) if f.endswith(".png"))[::3]
rgb = [Image.open(os.path.join(d, f)).convert("RGB").resize((1200, 720), Image.LANCZOS) for f in files]
# One palette from two frames side by side (3 s and 10.5 s), so both colours stay exact.
# The house colours go in as large swatches too, so the paper of the card can't drift to a neighbour.
TOKENS = ["#FAF8F3", "#1F1C1A", "#615B53", "#E8E3DA", "#3A3531", "#C9876A", "#CBC1B1", "#F3EFE7", "#B8613F"]
w, h = rgb[0].size
both = Image.new("RGB", (w * 3, h), "#FAF8F3")
both.paste(rgb[30], (0, 0)); both.paste(rgb[-1], (w, 0))
for i, col in enumerate(TOKENS):
    both.paste(Image.new("RGB", (w // 3, h // 3), col), (2 * w + (i % 3) * (w // 3), (i // 3) * (h // 3)))
q = both.quantize(colors=200, method=Image.Quantize.MEDIANCUT)
# Median cut averages its buckets, so the flat colours come out a shade off: put the exact tokens in the palette too.
exact = [c for t in TOKENS for c in (int(t[1:3], 16), int(t[3:5], 16), int(t[5:7], 16))]
# Drop median-cut entries within a few levels of a token: Pillow's palette lookup is coarse and would pick them.
near = lambda r, g, b: any(abs(r - exact[i]) + abs(g - exact[i + 1]) + abs(b - exact[i + 2]) < 24 for i in range(0, len(exact), 3))
mc = q.getpalette()[: 200 * 3]
entries = exact + [x for i in range(0, len(mc), 3) if not near(*mc[i:i + 3]) for x in mc[i:i + 3]]
pal = Image.new("P", (1, 1))
pal.putpalette(entries + [0] * (768 - len(entries)))
frames = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
out = os.path.join(here, "anim-prompt-caching.gif")
frames[0].save(out, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True, disposal=1)
print(len(frames), "frames,", round(os.path.getsize(out) / 1024), "KB", file=sys.stderr)
