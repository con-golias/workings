# Made by AI, owned by no one: what 12,853 US copyright filings admit

Workings for the X Article by Konstantinos Gkolias (@con_golias).

**Question.** Since March 2023, anyone registering a work that contains AI-generated material with the US Copyright
Office must say which part the AI made and exclude it from the claim. What do those public statements say?

**Answer in numbers** (all in `data/summary.json`, records read 9 November 2026): 17,979 records matched an AI phrase
(1,027 of them are recorded documents, not registrations); 12,853 have it in the applicant's own authorship statements (the rest only in a title, name or note).
1 in 1,021 registrations disclaimed AI material in 2023, 1 in 51 in 2026 Q1 (the last complete quarter). Of 8,083 book
(Text) registrations, 66.5% say the AI made only the images and 28.9% that it wrote some text; one literary agency has
590 of the 2,333 AI-text books. Of 2,202 music and sound-recording registrations, 86.6% say the AI made the music, not the
words (88.8% name music at all), and 4.0% that it wrote lyrics. 4.8% of all registrations name a tool (Suno 381, ChatGPT/OpenAI 131, Midjourney 71).

## Rerun

```bash
cd code
python fetch.py         # search + every full record -> data/ids.json, data/raw/ (not in this repo; 1-2 h, slow server)
python denominator.py   # all registrations per month and type of work -> data/denominator.json
python analysis.py      # data/summary.json, data/registrations.csv
python render.py        # article text from the template (numbers are tokens)
```
Figures: serve the folder (`python -m http.server 8797`), then `BASE=http://127.0.0.1:8797/charts PW=<playwright>
node charts/figures.mjs`; the video with `charts/video.mjs` and ffmpeg (command in the file).

## Files
- `data/ids.json`: every record id the search returned, with the phrases that found it.
- `data/denominator.json`: total registrations per month, by type of work (same catalogue).
- `data/registrations.csv`: one row per kept registration: number, date, type of work, class, claimant (organisations
  by name; private individuals as "(individual)"; a person's name inside any statement, after "by", "written by",
  "spoken by" and the like, as "[name]"), authors' countries, where the AI phrase sits, the excluded and
  included statements, the parts the AI made, the tools named, the title.
- `data/raw/` is not included: the full records hold claimants' street addresses and authors' birth years. `fetch.py`
  rebuilds it from the public API.
- `METHOD.md`: what counts, the denominator, the lag, the checks and the limits.

Source: US Copyright Office, Public Records System (publicrecords.copyright.gov), public records of registration.
