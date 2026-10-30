# Research: how many popular GitHub projects lock their releases, a year after GitHub made it possible

> The evidence behind the [X Article](https://x.com/con_golias/status/2116214265132564766) *"The OVHcloud attack still works on 9 in 10 popular GitHub projects"* by Konstantinos Gkolias (@con_golias), published 30 Oct 2026. Data pulled 30 Oct 2026.

## The question

GitHub's immutable releases became generally available on 28 October 2025. A release published with the setting on
can't have its files changed or deleted, and its tag can't be moved. On 19 October 2026 a hijacked account replaced the
files of existing OVHcloud CLI releases; OVHcloud's founder said the setting had not been enabled. How many of the
projects developers download from have it on, and what else do they give a user to check a download?

## Result

| | Ship software in latest release | Locked | Released since GA | Of those, locked | Nothing to check |
|---|---|---|---|---|---|
| Top 2,000 by stars | 518 | 50 | 464 | 50 (10.8%) | 218 (42.1%) |
| Top 500 by stars | 138 | 14 | 127 | 14 (11.0%) | 59 (42.8%) |
| Homebrew top 200 (install-on-request, 30 days) | 87 | 17 | 83 | 17 (20.5%) | 20 (23.0%) |

- **What a user can check (top 2,000):** locked 50; signed or attested but not locked 87; checksum only 163; nothing 218.
- **Changed after publication:** 23 latest releases in the top 2,000 had a file uploaded more than 24 hours after
  publication (added or replaced; the API can't tell which).
- **Owners:** 10.8% of 362 organisation projects locked, 7.1% of 156 personal ones.
- Every number is in `data/summary.json`; every project's row, with its release link, in `data/repos_top.csv` and
  `data/repos_brew.csv`.

## Rules (fixed before the full run; changes listed below)

- **List A:** the 2,000 most-starred repositories (GitHub search, split by star ranges). **List B:** Homebrew's 200
  most installed-on-request formulae over 30 days, mapped to a GitHub upstream from the formula's URL or homepage
  (76 have none).
- **Software:** the latest release carries an executable, installer or package, or an archive whose name carries an
  OS or CPU token. Docsets, slides, books and model files are excluded (122 releases in list A).
- **Locked:** the release's `immutable` field. **Checksum:** any asset name matching a hash file (SHA256SUMS,
  checksums.txt, *.sha256, shasum.txt, *.md5, b2sums, electron-builder's latest*.yml) or a 64-hex hash in the release notes.
  **Signature:** .sig, .asc, .minisig, .pem, .bundle, .sigstore(.json), .intoto.jsonl, .p7s.
  **Attested:** GitHub's attestations API returns a record for the first binary's digest.
- **Changed after publication:** an asset whose `created_at` is more than 24 hours after `published_at`; tags without
  a version number (rolling "nightly" tags) are left out.
- Named releases are described as facts with dates. Nothing here suggests that any file was tampered with.

## Run it

```bash
python3 code/collect.py top raw      # list A: latest releases, assets, attestations (gh CLI, free quota)
python3 code/collect.py brew raw     # list B: Homebrew top 200, GitHub upstreams
python3 code/fetch_bodies.py raw     # release notes
python3 code/fetch_assets.py raw     # every asset name
python3 code/analyze.py raw data     # summary.json and the CSVs
```

`raw/` holds what the collectors saved on 30 Oct 2026 (latest releases, every asset name, release notes), so
`analyze.py` reproduces every number without calling the API again.

## Where it could be wrong

Stars are not installs; only the latest release is read; a checksum on an unlocked page can be replaced along with the
binary; hashes kept on a project's own website are not seen. Details in the article.

## Changes to the rules, in order

1. After the first run the "software" test let in content (page bundles, slide PDFs, a docset, model files), so
   names with docset, slides, book or model were excluded and archives need an OS or CPU token. 122 releases dropped.
2. Hashes printed in release notes (64 hex characters) count as a checksum.
3. Before writing: one checksum rule over every asset name, which added `shasum.txt` and electron-builder's
   `latest*.yml`. Nothing to check fell from 51% to 43%.
4. Before publishing: `.md5` and BLAKE2 files added to the rule (asdf ships `.md5` files). Top 2,000: 222 → 218;
   Homebrew: 21 → 20.

GitHub's own per-asset `digest` is not counted: it is computed from the file that is there now.
