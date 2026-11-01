# Research: AI-assisted patches in the Linux kernel, 2026

> The evidence behind the X Article *"AI now helps write 1 in 4 Linux kernel bug fixes. Its own patches need fixing no
> more often"* by Konstantinos Gkolias (@con_golias), published 1 Nov 2026. Data read on 31 Oct 2026.

## The question

Since Linux 7.0, kernel developers add `Assisted-by: AGENT:MODEL` to a patch when an AI tool helped write it, and every
bug fix names the commit that caused the bug in a `Fixes:` line. Joined, the two answer three questions: how much of the
kernel's work is AI-assisted, whether AI-assisted patches need fixing more often, and which bugs AI-assisted fixes repair.

## Result

| | AI-assisted | Everything else |
|---|---|---|
| Share of bug fixes (commits with `Fixes:`) carrying the tag, October 2026 | **912 of 3,600 (25.3%)** | |
| Fixed by a later commit within 90 days (commits 1 Jan – 2 Aug 2026) | 2.8% (57 of 2,069) | 3.5% (1,839 of 52,495) |
| Same 241 authors, with and without the tag | 2.9% (54 of 1,891) | 3.7% (247 of 6,606) |
| Same subsystem (expected from untagged commits with the same title prefix) | 47 observed | 56.8 expected |
| Same month (expected from untagged commits of the same month) | 57 observed | 61.4 expected |
| Same kind of commit, fix or not (added after review, not in the wording rule) | 57 observed | 66.8 expected |
| Reverted within 90 days | 0.19% (4) | 0.24% (126) |
| Median age of the bug, fixes merged May–Oct 2026 | 4.2 years | 2.5 years |
| Bugs more than 10 years old, same fixes | 24.2% | 13.5% |

- Same-author ratio (tagged / untagged fix rate): 0.76, 95% author-cluster bootstrap 0.52–1.04 (1,000 resamples, seed 2026).
- Among bug-fix commits only, the 90-day rate is 3.1% tagged vs 2.5% untagged; at 30 and 60 days it is lower for tagged.
- Bug age without the ten busiest taggers: median 3.9 years; same 329 authors with and without the tag: 4.8 vs 3.7 years.
- Every number is in `data/summary.json` and `data/bug_age_robust.json`.

## The test, written down before the final run

- **Population:** non-merge mainline commits with a commit date from 1 Jan 2026 to (last commit − 90 days).
- **Outcome:** a later mainline commit names it in `Fixes:` within 90 days of its commit date.
- **Comparisons:** overall; same authors; subsystem-matched; month-standardised; 30/60/90-day windows; fixes vs non-fixes.
- **Wording rule:** "no more often" only if the tagged rate is at or below the untagged rate in the overall, same-author,
  subsystem and month comparisons, and the upper end of the same-author bootstrap interval is below 1.25. "Less often"
  only if that upper end is also below 1.0. Result: all four at or below, upper end 1.04, so "no more often".
- No result is broken down by tool or model.

## How

1. Clone the commit history without file contents:
   `git clone --bare --filter=tree:0 --shallow-since=2025-06-01 https://github.com/torvalds/linux.git linux.git`
   (31 Oct 2026: 126,263 non-merge commits.)
2. `code/parse.py linux.git commits.json`: sha, author, author and commit dates, subject, `Assisted-by:` values,
   `Fixes:` targets, `This reverts commit` targets, `Reported-by: Sashiko`, `Cc: stable`.
3. `code/target_dates.py commits.json data/target_dates.json`: author dates of the commits named in `Fixes:` lines of
   fixes merged May–Oct 2026 that are older than the clone, from GitHub's GraphQL API (needs `gh auth login`;
   9,888 found, 25 not found). Only the bug-age numbers use this.
4. `code/analysis.py commits.json linux.git data data/target_dates.json`: writes `summary.json`, `monthly.csv` and
   `tagged_commits.csv` (every tagged commit with its outcome).
5. `code/robust_age.py commits.json linux.git data data/target_dates.json`: the bug-age checks.
6. `code/subsystems.py commits.json data/subsystems.json`: the share of each subsystem's fixes that carry the tag
   (subsystems with ≥ 80 fixes, May–Oct 2026) and the bug kinds named in fix titles.

`Fixes:` prefixes are resolved against the clone by prefix match; none was ambiguous. References to commits older than
the clone don't affect the 90-day comparison, since every commit compared is from 2026.

## Limits

- `Assisted-by:` is self-reported; untagged AI-assisted patches sit in the untagged group.
- 90 days measures early detection, not a lifetime bug rate. Not every fix carries `Fixes:`.
- Subsystem is the commit title's prefix up to the first colon, the kernel's convention, not the files touched.
- Bug age runs from the buggy commit's author date to the fix's commit date (when a maintainer committed it, not when it reached mainline).
- No patch sizes: the clone has no file contents.
- The tag requirement is being dropped (Maintainers Summit, 8 Oct 2026), so later data will be thinner.

## Data

| File | What |
|---|---|
| `data/summary.json` | Every figure and table in the article |
| `data/monthly.csv` | Per month: commits, tagged, fixes, tagged fixes, Sashiko-reported fixes, tagging authors |
| `data/tagged_commits.csv` | All 6,372 tagged commits in the clone: sha, date, author email, subject, tag, outcome |
| `data/target_dates.json` | Author dates of older commits named in `Fixes:` lines |
| `data/bug_age_robust.json` | The bug-age checks |
| `data/subsystems.json` | Tag share of fixes per subsystem, who tagged them, bug kinds by title keyword |

The kernel's history is public; commit authors' names and emails are as they appear in it.
