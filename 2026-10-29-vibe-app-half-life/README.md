# Research: how long do new apps last, with and without AI app builders?

> The evidence behind the X Article *"Four in five new apps go quiet within a month. AI didn't change that"* by
> Konstantinos Gkolias (@con_golias), 29 Oct 2026. Data read on 28 Oct 2026.

## The question

Apps built with Lovable, v0 and Google AI Studio in October 2025: how long did they keep changing, and are they
still online a year later? And how does that compare with ordinary new apps created on the same days?

## Result

One repository per account. Share of apps with a change made at least N days after the repository was created
(dependency and deploy bots removed). 95% bootstrap intervals are in `data/summary.json`.

| Still changing after… | Lovable (5,260) | v0 (1,589) | Ordinary React apps (2,519) |
|---|---|---|---|
| 30 days | 17.4% | 19.8% | 21.5% |
| a change between 28 Jul and 28 Oct 2026 | 3.2% | 3.7% | 3.9% |
| deployed apps still answering (HTTP 200) | 76.9% | 79.7% | 69.1% |

- About four in five new apps had their last change within the first month, whether a builder made them or not.
- Lovable is 4.1 points more likely to have gone quiet by 30 days (the intervals do not overlap). v0 sits in
  between.
- A year on, the builders and the ordinary React apps are within each other's intervals.
- **AI Studio is left out of the activity comparison.** In October 2025 its GitHub link was export-only, so later
  edits rarely reached the repository. It appears only in the "online" check (80.9% of 753 still answer).
- **Leaving the builder:** after the first day, 22.4% of Lovable and 31.1% of v0 apps got a commit not made by the
  builder or another AI app tool.
- 4.8% of random new JS/TS repositories (with a `package.json`) were builder exports.

## Samples

| Group | How | Repositories |
|---|---|---|
| Lovable | README search "Lovable project" / `lovable.dev/projects`, per day 1–24 Oct 2025, all pages | 17,282 (random 6,000 read) |
| AI Studio | README search "AI Studio app", same | 12,279 (random 4,000 read) |
| v0 | README search "stay in sync with your deployed chats", same | 1,913 (all read) |
| Ordinary | 400 random pages of `GET /repositories?since=<id>` in the ID range of 1–24 Oct 2025 | 31,805 → 5,238 with `package.json` → builder exports removed; React subset 2,519 accounts |

- **Census:** no day returned more than 874 results, so the builder searches are complete.
- **Old uploads dropped:** repositories whose history starts more than 14 days before creation (decidable when all
  commits were read).

## Rules

- **Not activity:** dependency and deploy bots (Dependabot, Renovate, GitHub Actions, vercel[bot], …).
- **Activity:** builder bots (lovable-dev[bot], v0[bot], the v0 login), because they are a person editing in the
  builder.
- **Counted separately:** other AI app tools (Orchids, Builder.io, Emergent, …).
- **What was read:** the latest 30 commits per repository. The last change is always among them.
- **Online:** an HTTP request on 28 Oct 2026 to the repository's homepage or the first deploy-host URL in its
  README; status 200.

## Limits

- **Deleted repositories are invisible**, so survival is overstated in every group.
- **Only GitHub-connected builder projects are visible.** That is roughly one Lovable project in 230 (an order of
  magnitude, from figures of different months).
- **A Lovable or v0 repository is created when GitHub is connected**, which may be after the project started.
- **"Ordinary" means not made with these three builders.** Some were surely written with other AI tools.
- **Online means the page answers**, not that it works or is used.

## Rerun

GitHub CLI (`gh auth login`), Python 3.11+, free API quota only.

```
export RAW=raw
python3 code/collect_builders.py
python3 code/collect_v0.py
python3 code/find_id_range.py          # prints the ID range; set LO/HI in collect_baseline.py if it differs
python3 code/collect_baseline.py
# a random 6,000 Lovable / 4,000 AI Studio from census_repos.json -> raw/builder_sample.json (list of names)
python3 code/fetch_activity.py builder_sample.json builder_act.json
python3 code/fetch_activity.py v0_sample.json v0_act.json
python3 code/fetch_activity.py base_sample.json base_act.json
python3 code/extract_urls.py
python3 code/check_online.py
python3 code/check_online_v0.py
python3 code/analyze.py raw
python3 code/export_lists.py raw
```

Search results and repositories change over time, so a rerun will not match exactly. Every repository used here is
in `data/repos.csv`, with its creation date, last change, commit count, URL and HTTP status.
