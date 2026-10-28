# Research: which libraries do new projects with an AI agent's trace start with?

> The evidence behind the X Article *"In new React apps built with an AI agent, axios is down to 13%. Two years ago
> it was in 80%"* by Konstantinos Gkolias (@con_golias), 28 Oct 2026. Data collected 27–28 Oct 2026.

## The question

Coding agents now set up many new projects, and every package they install is a choice. **Do new JavaScript and
TypeScript projects with an AI agent's trace start with different libraries from those without one, and from new
projects of two years ago?** Measured from `package.json` files, not surveys.

## Result

Shares inside a category (among the projects that use any package of that category), one repository per account,
95% bootstrap intervals in `data/summary.json`.

| | Oct 2024 | Oct 2026, no trace | Oct 2026, agent trace |
|---|---|---|---|
| React apps: axios | 80.3% | 35.2% | **12.7%** |
| React apps: TanStack Query | 27.7% | 63.9% | **87.9%** |
| Database layer: mongoose (MongoDB) | 42.8% | 22.0% | **6.3%** |
| Database layer: drizzle | 12.2% | 34.0% | **58.3%** |
| Database layer: prisma | 34.4% | 32.0% | 30.3% |
| Hosted backend: firebase | 44.0% | 24.4% | 14.6% |
| Hosted backend: supabase | 24.9% | 73.2% | 73.5% |

- **Already decided in 2024** (zod, tailwindcss, lucide-react, vitest, vite): both 2026 groups are within a few
  points of each other.
- **Firebase** is not an agent effect. Untraced projects that call the Gemini SDK use Firebase in 78.3%; without
  them, untraced Firebase is 12.0%.
- **Newer challengers** (Biome, oxfmt) are more common with an agent's trace. The traced projects are further along
  in whichever direction a category is moving.

## Samples

| Sample | How | Repositories | Usable `package.json` |
|---|---|---|---|
| Oct 2024 | repo search `created:<day> language:TypeScript\|JavaScript fork:false`, 1–24 Oct, ≤300/language/day, default order; `package.json` read at the last commit on or before 30 Nov 2024 | 14,396 | 8,923 |
| Oct 2026 (main) | same search and order, 1–24 Oct 2026; HEAD | 14,368 | 7,046 (3,543 traced) |
| Oct 2026 (check) | same, "recently updated" order | 14,371 | 7,792 (4,679 traced) |
| Claude Code / Cursor / Codex | commit search for each agent's co-author line, ≤1,000 commits/day | 7,286 / 6,114 / 1,837 | direction check only |

**Usable** means created in the month searched, a root `package.json`, at least three dependencies, and not a fork.

**Traced** means any of the following:

- an agent co-author line in the last 50 commits (Claude, Cursor, Codex);
- an agent instruction file at the root (`CLAUDE.md`, `.claude`, `AGENTS.md`, `.cursor`, `.cursorrules`,
  `.codex`, `GEMINI.md`, `.windsurfrules`, `.windsurf`, `.kiro`, `.trae`);
- an app-builder signature (`lovable-tagger`, an AI Studio / Lovable / Bolt / v0 README, `.replit`, `.idx`).

*Untraced is not "written by a person":* Copilot leaves no trace that can be read here, and co-author lines can be
switched off. The 2024 sample, using the same file tests (no commit history was read for 2024), has 94 traced
repositories of 8,923 (1.1%).

## Checks (all in `data/summary.json`)

- **Instruction files:** dropping projects whose `CLAUDE.md`, `AGENTS.md`, `.cursorrules` or `GEMINI.md` names a
  library of the category leaves the traced shares unchanged (axios 13.0%, mongoose 7.2%, drizzle 56.8%).
- **Project depth:** in the third with the most dependencies (18+), the axios and drizzle gaps hold; the mongoose
  intervals overlap.
- **Template clones:** keeping one repository per identical dependency set moves no share by more than one point.
- **Starters:** create-t3-app packages appear in 6 traced and 5 untraced projects.
- **Sample order:** the traced shares agree across the two 2026 samples; the untraced shares move more. The gap
  between the two 2026 groups should be read as a range.
- **Not used:** npm download counts (they measure the installed base, transitive installs and CI); co-author counts
  as agent market share (they measure defaults).

## Rerun

Requires the GitHub CLI (`gh auth login`), Python 3.11+, free API quota only. About three hours, mostly waiting for
search rate limits.

```
export RAW=raw
python3 code/collect_control_2024.py
python3 code/collect_control_2026_bestmatch.py
python3 code/collect_claude_and_control_2026.py
python3 code/collect_agent_trailer.py cursor "cursoragent@cursor.com"
python3 code/collect_agent_trailer.py codex "Co-authored-by: Codex"
python3 code/fetch_meta_asof_2024.py raw/ctl24_repos.json raw/ctl24_meta.json
for s in ctlbm ctl agent cursor codex; do python3 code/fetch_meta.py raw/${s}_repos.json raw/${s}_meta.json; python3 code/fetch_history.py raw/${s}_meta.json raw/${s}_hist.json; done
python3 code/fetch_instructions.py raw/ctlbm_meta.json raw/ctlbm_instr.json
python3 code/analyze.py raw
python3 code/export_lists.py raw
```

GitHub search results change over time, so a rerun will not reproduce the exact repository lists. The lists used
here are in `data/repos_*.csv`, each with its dependency count and the category packages it lists.

## Files

- `code/categories.py`: the categories and the packages in each.
- `code/tags.py`: scaffold, agent-file and app-builder signatures.
- `code/analyze.py` → `data/summary.json`: every number in the article.
- `data/repos_2024.csv`, `data/repos_2026.csv`, `data/repos_2026_recently_updated.csv`: one row per usable
  repository.
