# Method: security-relevant fixes in Claude Code's 2026 changelog

**Source.** `CHANGELOG.md` of anthropics/claude-code, read 20 November 2026 (445 sections, 0.2.21 to 2.1.329). Each
section dated by the npm publish time of that version (`@anthropic-ai/claude-code`). 2026 = 265 sections dated by npm (2.1.43 and 2.1.46 have no npm time and are left out); npm lists 286 versions in 2026.

**What counts (written 20 Nov, applied to every line).** A "Fixed", "Security:" or "Hardened" bullet counts when it
reports that something (a command, tool call, file read or write, network request, setting, plugin, hook or subagent)
did, or could, get past a control that should have stopped it or asked: the permission prompt and its allow/ask/deny
rules, the OS sandbox, workspace trust and consent dialogs, organisation (managed) policy, a blocking hook, plan mode,
--restricted, path containment. Not counted: fixes where the control was too strict, display-only fixes, credential
printing, "Changed…"/"Added…"/"Improved…" design tightenings.

**How lines were found.** Keyword pools over every bullet (permission, sandbox, deny, trust, policy, symlink, bypass…),
then every candidate read by hand (209 in pass 1, 1,071 more in pass 2; the low-yield part of pass 2 was read after a
filter). Codes per entry: control, precondition (none named / needs a loosened mode / a route through auto mode as a default (from 2.1.228) needing nothing loosened, read by hand / sandbox auto-allow), platform flag;
keyword-proposed (`code/recode_draft.py`), hand-reviewed (`code/apply_codes.py`). `code/analysis.py` asserts that every
counted text sits verbatim under its version.

**Recall.** Ten whole releases read bullet by bullet (461 bullets): 27 counted, 8 missed under the rule, plus three borderline
lines: roughly three in four found. The count is a floor; the missed lines are not added. **Precision:** 40 random
entries plus 4 unclear-direction lines judged against the rule: 43 hold, 1 cut (2.1.325, direction unclear).

**Advisories.** GitHub advisory database (package @anthropic-ai/claude-code, 30) and the repository's security page
(36; 2 more for Claude Code, 4 for Claude Desktop). Each advisory patched in a 2026 release was looked up in the
changelog from about 15 versions before to 5 after its patched version (`data/advisory_join.tsv`).

**Limits.** An entry is a fix, not an incident: nothing here shows any was exploited. One bullet can hold several
fixes. The changelog also covers VS Code, cloud sessions and other surfaces. Q4 is partial (to 19 Nov). The share per
100 changelog lines rose, but the changelog itself grew from 25 lines a month (March 2025) to about 1,800 (September
2026), and early-2026 lines were terser, so "the changelog reports more" is the claim, not "more gaps exist".

**Symlink layers.** The 25 counted entries that mention a symbolic link, a junction or a link swapped mid-read were
each read and assigned by hand to one layer (`code/analysis.py`, `HAND`): file tools 7; settings, CLAUDE.md and the
config folder 5; worktrees and sessions 4; the OS sandbox 3; permission rules on a path 2; plugins 2; shell commands 1;
undo (/rewind) 1. The script asserts that every assignment matches exactly one entry and that all 25 are assigned.

**Advisory descriptions.** For each of the 13 advisories patched in a 2026 release, the full description was read
(GitHub advisory API; the repository's security page for the two repo-only ones) and its distinctive terms were
searched in the changelog from 15 versions before to 5 after the patched version. None changed category.

**Two lookups named in the text.** Version 2.1.88 (where Anthropic told SecurityWeek a sandbox fix shipped) has an npm
publish record but is no longer listed among npm's versions and has no changelog section; no proxy or SOCKS line
appears in 2.1.73–2.1.95. Version 2.1.32 (where Anthropic told Wiz a symlink warning shipped) was read in full: 12
lines, none about symlinks or the edit dialog.

**Fetch.** `code/fetch.py` downloads today's CHANGELOG.md and npm publish times (tested 21 Nov into a separate folder:
the npm times match `data/cc_times.json` for every version). The changelog grows daily; the numbers here are from the
20 November copy.
