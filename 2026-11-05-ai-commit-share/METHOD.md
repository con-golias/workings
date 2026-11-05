# Conventions

- **Numerator:** `"Co-Authored-By: Claude"` (commit-search phrase match; all 100 commits read on 3 Nov carried the
  literal line). Commits authored by the `claude` account without the line are counted separately, not added.
- **Denominator:** the date qualifier alone. No spam subtraction by search term (the spam phrases overlap and return
  incomplete counts); flooded days and weeks are excluded from shares instead.
- **Dates:** committer date, UTC. Weeks run Monday–Sunday.
- **Incomplete counts:** a window flagged `incomplete_results` is summed from single days; a single day still flagged is
  kept and logged (probes: within 0.05–2.2% of the sliced sums).
- **Projections:** compound daily growth from 2 Feb to 3 Nov 2026 (Claude and the index separately), extended to
  31 Dec; and the least-squares trend of the 22 calm days. Scenarios, not forecasts.
- **Scheduled-looking commits:** author name containing `[bot]` or `github-actions`, or a message starting with a date,
  "update", "auto", "refresh", "sync", "daily", "data", "status", "bump", "chore: update" or "[skip ci]". Crude; the
  same rule runs on both samples.
- **Samples:** pages of the search's default (relevance) order within random hours, not random draws. Stars and
  creation dates via GraphQL on 5 Nov 2026.
