# npm packages that write into AI coding agents' configuration at install time

Workings for the X Article *"29 npm packages write into your AI agent's setup the moment you install them. Postman's CLI
is one"* (Konstantinos Gkolias, [@con_golias](https://x.com/con_golias), November 2026).

## Rerun the first check

```bash
curl -s -H 'Accept: application/vnd.npm.install-v1+json' https://registry.npmjs.org/postman-cli \
  | jq '.versions[."dist-tags".latest].hasInstallScript'
```

## Pipeline (Python 3, standard library)

| Step | Script | Output |
|---|---|---|
| 1. Agent packages: npm search, top 1,000 per keyword (10 keywords); control: wooorm/npm-high-impact | `code/universe.py` | `data/universe.json` |
| 2. Latest version: install script? scripts, tarball | `code/screen.py` | `data/install_scripts.json` |
| 3. Download tarballs (not in this repo), follow the install command's files and their relative imports (one level), flag agent-config paths | `code/scan.py` | `data/scan.json` |
| 4. Weekly downloads of flagged packages | `code/downloads.py` | `data/downloads.json` |
| 5. Review sheet (signals for reading by hand) | `code/sheet.py`, `code/review.py`, `code/show.py` | `data/sheet.json` |
| 6. Hand verdicts for the 55 most-downloaded flagged agent packages | `code/verdicts.py` | `data/verdicts.json` |
| 7. postman-cli: which releases append to CLAUDE.md / AGENTS.md | (see notes in the file) | `data/postman_cli_versions.json` |
| 8. Every number in the article | `code/analyze.py` | `data/summary.json` |
| 9. Figures | `charts/figures.html` (+ `charts/figures.mjs`) | `charts/*.png` |

`code/probe_*.py` are the first probe of 5 Nov (1,855 packages), kept for the record.

## Tests in an empty home

With `HOME` and `USERPROFILE` pointing at an empty folder that contains `.claude/` (with a one-line `CLAUDE.md`) and
`.codex/`:

- `npm install -g --prefix <tmp> postman-cli@1.86.0`: `CLAUDE.md` gains the Postman block; `~/.codex/AGENTS.md` is created with it.
- In an empty project, `npm install karajan-code`: `~/.claude.json` gains an `mcpServers.karajan-mcp` entry.
- npm 11.17: a test postinstall ran and printed nothing. npm 12.2.2: blocked as a dependency and with `-g`.

## Limits

A ranking, not a census; one level of imports; dynamic paths missed; 55 read by hand, 69 small ones not read; latest
versions on 6 Nov 2026 only. Tarballs are not included: they are third-party code, and one contains a credential.
