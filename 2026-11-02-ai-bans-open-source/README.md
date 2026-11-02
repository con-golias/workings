# Research: open-source projects that banned AI code, 2018–2026

> The evidence behind the X Article *"Banning AI code didn't cost open-source projects their contributors. It didn't
> keep AI out either"* by Konstantinos Gkolias (@con_golias). Data read on 2 November 2026.

## The question

Gentoo (14 Apr 2024), NetBSD (May 2024) and QEMU (24 Jun 2025) banned contributions made with AI code generators.
Did the bans change how many new contributors arrived, compared with projects that didn't ban AI (nixpkgs, FreeBSD,
Linux, LLVM)? And did AI-attributed commits land in the banned projects anyway?

## Result

| Project | New contributors, after ÷ before | Comparison mean | Effect | Effect at a fake date two years earlier |
|---|---|---|---|---|
| Gentoo | 0.80 | 1.37 | 0.58 | 0.61 |
| NetBSD | 1.00 | 1.37 | 0.73 | 0.34 (0–4 new committers a half: noise) |
| QEMU | 1.19 | 1.29 | 0.92 | 0.68 |

- No measurable effect of the bans on newcomers. Gentoo's decline began in 2022 H2, before its ban; without 2026 H1
  (after it moved pull requests to Codeberg) its effect is 0.65.
- 2026 newcomers who tagged an AI tool on a 2026 commit: Linux 483 / 3,599 (13.4%), LLVM 280 / 1,635 (17.1%),
  nixpkgs 290 / 2,021 (14.3%).
- AI trailers landed after the ban: QEMU 30 (one series, Warner Losh, merged 18 Sep 2026), NetBSD 1 (an upstream BIND
  import), Gentoo 0, GCC 164 of 3,028 since 29 Jul 2026 from 27 authors (GCC's policy requires the tag and allows
  disclosed insignificant changes and tests).
- Active contributors (secondary), real vs fake date: Gentoo 0.68 vs 0.76, QEMU 0.86 vs 0.79, NetBSD 0.71 vs 0.67.
- Every number is in `data/numbers.json`.

## Design (written before the full run)

- New contributor = an author e-mail (lower-cased) whose first commit since 2018-01-01 falls in that half-year;
  2018–2019 burn-in; bots excluded.
- Effect = banned project's (mean new per half after the ban ÷ mean in the four halves before) divided by the mean of
  the same ratio for the comparison projects over the same calendar halves.
- Wording rule: below 0.85 "lost", 0.85–1.15 "no measurable loss", above 1.15 "gained".
- **Amendment after the first run (disclosed):** the same measure at a fake ban date two years earlier (`placebo.py`),
  because Gentoo's decline visibly predates its ban. The article reports both.

## How

1. For each project: `git clone --bare --filter=tree:0 --shallow-since=2018-01-01 https://github.com/<owner>/<repo>`
   (gentoo/gentoo, NetBSD/src, qemu/qemu, NixOS/nixpkgs, freebsd/freebsd-src, llvm/llvm-project, torvalds/linux,
   gcc-mirror/gcc), then `git log --format='%ae|%an|%ad|%cd' --date=short > <owner>_<repo>.log`.
2. `code/analyze.py <logdir> data/summary.json`: series and effects.
3. `code/placebo.py <logdir> data/placebo.json`: the fake-date test.
4. `code/trailers.py <dir with .git and .log> data/trailers.json`: AI-attribution trailers (strict rule in the file).
5. `code/numbers.py <logdir>`: gathers everything into `data/numbers.json`.

## Limits

E-mail ≠ person; NetBSD and FreeBSD record committers; Gentoo's decline predates its ban; the placebo was added after
the first run; 2026 H2 is partial (to 2 Nov) and not used in any effect; tags are voluntary, so every AI share is a floor;
GCC allows part of the tagged use.
