# Humanoid robots at work in 2026: who buys them, what they do, what is planned

Workings for the X Article by Konstantinos Gkolias (@con_golias).

**Question.** Which companies and industries use humanoid robots now, what do the makers' own regulatory filings say
about who buys them, what do the money and the five-year plans say, and how much human work do the documented
deployments add up to?

**Answer in numbers** (all in `data/summary.json`; sources read 21 November 2026):
- IDC: about 25,000 humanoids shipped in H1 2026 (+432.1%); buyers in China took over 19,000 (77.9%); Chinese makers
  built over 95%. Research and education, shows and exhibitions and government data-collection centres took 83.8% of
  shipments in 2025 and 69% in H1 2026.
- Unitree (reply to the Shanghai Stock Exchange, 20 Mar 2026), humanoid revenue Jan–Sep 2025: research and education
  73.60%, commercial and consumer 17.39%, "industry" 9.01%; enterprise guided tours were about 50–70% of "industry", so
  factory and inspection work was at most 2.7–4.5% of humanoid revenue.
- Agility (SEC S-4/A, 30 Sep 2026): pipeline ~28,000 robots deployed by 2030; the fairness adviser's schedule ~7,000
  (25%). 2025 sales $1,782K, 58% from one investor that bought five robots. Nine months to 30 Sep 2026 (8-K/A,
  13 Nov 2026): sales $361K, net loss $458.7M.
- Capacity the makers announced: 1,058,000 a year (Tesla 1,000,000 of it) against about 50,000 a year shipped.
- Work done: Figure 02 at BMW, 1,250+ hours = 0.62 of a 2,000-hour working year; Agility's Digit, 65,000+ hours at all
  customers = 32.5 working years.
- IDC's 2030 forecast (750,000 a year) = 0.15% of the ILO's ~500 million manufacturing workers: one per 667.

## Rerun
```bash
python code/compute.py             # data/inputs.json -> data/summary.json (every derived number)
python code/render.py              # article text from the template (numbers are tokens)
python -m http.server 8861         # then, from another shell:
BASE=http://127.0.0.1:8861/charts PW=<playwright> node charts/figures.mjs            # the 13 figures
BASE=http://127.0.0.1:8861/charts PW=<playwright> VIDEO=video-1 SECONDS=21 FRAMES=<dir> node charts/video.mjs
python code/shot_unitree.py        # needs data/raw/unitree_OE27.pdf
PW=<playwright> node code/shot_agility.mjs   # needs data/raw/agility_s4a.htm
```
Videos: `ffmpeg -framerate 30 -i <dir>/%04d.png -c:v libx264 -crf 16 -pix_fmt yuv420p charts/video-1.mp4`.

## Files
- `data/inputs.json`: every input number with its source and whether it is primary or secondary.
- `code/compute.py`: every derived number (shares, worker-years, coverage, capacity ratio).
- `data/summary.json`: all published numbers.
- `charts/`: figure and video sources (HTML/SVG) and the rendered PNG/MP4 files; two source screenshots.
- `METHOD.md`: where each number was read, definitions, limits. The source documents themselves are public and are
  not copied here; METHOD.md says where to get them.
