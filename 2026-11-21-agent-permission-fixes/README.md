# Your deny rules can miss. Claude Code's 2026 changelog lists 44 entries where a rule didn't hold

(268 entries in all where a safety check let something through.)

Workings for the X Article by Konstantinos Gkolias (@con_golias).

**Question.** Claude Code's public changelog lists fixes release by release. How many of the 2026 fixes say that a safety
check (the permission prompt, allow/ask/deny rules, the OS sandbox, workspace trust, organisation policy, hooks, plan
mode, path boundaries) let something through that it should have stopped or asked about? And how do they compare
with Anthropic's security advisories for Claude Code?

**Answer in numbers** (all in `data/summary.json`, changelog and advisories read 20 November 2026): 268 changelog
entries in 2026 (a floor: about three in four found in a full read of ten releases), in 96 of the 265 sections dated
2026. By check: permission check 71, deny/ask rules and read blocks 44, organisation policy 44 (+7 admin-only), path
boundaries 33, OS sandbox 30, hooks 14, trust and consent 14, plan mode 8, command injection 3. 30 need a loosened
mode, 8 have a route through auto mode as a default, 5 sandbox auto-allow, 225 neither. 25 involve a symbolic link. Of 13 advisories patched in 2026 releases, 3
have a changelog line that clearly describes the fix, 1 a possible match, 1 a partial one, 8 none found. Advisory lag:
median 46 days (6 to 153, 31 dated advisories).

## Rerun

```bash
python code/which_fixes.py 2.1.250   # counted 2026 entries fixed after your version (needs only data/entries_public.json)
python code/fetch.py                 # the changelog and npm times as of today (the numbers here are from the 20 Nov copy)
python code/analysis.py              # data/entries_coded.json + advisory files -> data/summary.json
```
`analysis.py` needs `data/entries_coded.json`, which is not in this folder (see below). To check a row without it: fetch
the changelog, take the bullet under that row's version, and compare the first 12 characters of its SHA-1 (UTF-8, the
bullet text without the leading "- ") with `text_sha1`.

Figures: serve the folder (`python -m http.server <port>`), then `BASE=http://127.0.0.1:<port>/charts PW=<playwright>
node charts/figures.mjs`; the video with `charts/video.mjs` and ffmpeg (command in the file); the GIF with `charts/gif.mjs`.

## Files
- `code/rule.py`: the counting rule, as applied to every line.
- `code/recode_draft.py`, `code/apply_codes.py`: keyword-proposed codes and the hand review that overrides them. They
  show how each entry was coded; they read files built from the changelog text, which are not in this folder.
- `data/entries_public.json`: one row per counted entry: version, date (npm), control, precondition, platform flag, and
  a 12-character SHA-1 of the changelog line instead of its text. 270 rows: the 268 dated 2026, plus 1.0.120 and
  1.0.124 (September 2025), which are outside the count; `code/which_fixes.py <version>` reads it and counts the counted 2026 entries fixed after that version (the
  article's "How far behind is your version?" section prints this file and its output).
- `data/advisory_join.tsv`: each advisory patched in a 2026 release, its patched version and the changelog match.
- `data/gadv__anthropic-ai_claude-code.tsv`, `data/adv_patched.tsv`, `data/adv_repo_only.tsv`: the advisories.
- `METHOD.md`: what counts, how lines were found, recall and precision checks, the advisory join, the limits.

- `data/cc_times.json`: npm publish time of every version, used to date each changelog section.
- `charts/`: the figures, the cover, the opening video and the GIF, with the pages and scripts that draw them.

Not here: the changelog text itself, and `data/entries_coded.json`, which holds each counted line verbatim. The
changelog is Anthropic's; `code/fetch.py` downloads it.

Sources: anthropics/claude-code CHANGELOG.md; npm registry publish times; GitHub advisory database and the
repository's security advisories page; Claude Code documentation (permissions, sandboxing, security).
