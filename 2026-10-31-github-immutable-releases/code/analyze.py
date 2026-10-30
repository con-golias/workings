# Every number in the article comes from here. Inputs: RAW/top.json (list A) and RAW/brew.json (list B), written by
# collect.py. Outputs: data/summary.json, data/repos_top.csv, data/repos_brew.csv.
#   python3 code/analyze.py RAW data
import csv, json, os, re, sys
from datetime import datetime

RAW, DATA = sys.argv[1], sys.argv[2]
GA = "2025-10-28"  # immutable releases generally available
# Software, not content (rule tightened 30 Oct after the first run, see README): an executable, installer or package, or an
# archive whose name carries an OS or CPU token. Book PDFs, docsets, model zips and page bundles are out.
PKG = re.compile(r"\.(exe|msi|msix|dmg|pkg|deb|rpm|apk|aab|appimage|jar|whl|vsix|run|snap|flatpak|nupkg|gem|xpi|crx)$", re.I)
ARCHIVE = re.compile(r"\.(zip|tar\.gz|tgz|tar\.xz|txz|tar\.zst|tar\.bz2|7z|bin)$", re.I)
OSARCH = re.compile(r"(linux|darwin|mac|osx|windows|win(32|64)?\b|freebsd|android|ios|amd64|x86_64|x64|arm64|aarch64|i386|386|armv\d|riscv)", re.I)
BARE = re.compile(r"(linux|darwin|macos|windows|freebsd)", re.I)
SEMVER = re.compile(r"\d+\.\d+")
HEX64 = re.compile(r"\b[0-9a-fA-F]{64}\b")


def is_software(name):
    if re.search(r"docset|slides|book|model", name, re.I):  # documentation and model bundles, whatever their OS token
        return False
    return bool(PKG.search(name)) or (bool(ARCHIVE.search(name)) and bool(OSARCH.search(name))) or ("." not in name[-6:] and bool(BARE.search(name)))


BODIES = {}


def pct(a, b):
    return 100.0 * a / b if b else 0.0


def software(r):
    return r.get("release") and any(is_software(n) for n in (r.get("downloads") or []))


def rolling(r):
    return not SEMVER.search(r.get("tag") or "")


ASSETS = {}
CHECKSUM = re.compile(r"(sha256|sha512|shasum|checksum|md5|blake2|b2sums?|digests?\b|hashes|sums?\.txt$|\.sha\d+(sum)?$|^latest[-\w]*\.ya?ml$)", re.I)
SIGNATURE = re.compile(r"\.(sig|asc|minisig|pem|bundle|sigstore|sigstore\.json|intoto\.jsonl|p7s)$", re.I)


def has_checksum_file(r):
    return any(CHECKSUM.search(n) for n in (ASSETS.get(r["repo"]) or [])) or r["checksum_file"]


def has_signature_file(r):
    return any(SIGNATURE.search(n) for n in (ASSETS.get(r["repo"]) or [])) or r["signature_file"]


def notes_checksum(r):
    return bool(HEX64.search(BODIES.get(r["repo"]) or ""))


def checkable(r):
    return r["immutable"] is True or has_checksum_file(r) or has_signature_file(r) or bool(r.get("attestation")) or notes_checksum(r)


def block(rows):
    elig = [r for r in rows if software(r)]
    imm = [r for r in elig if r["immutable"] is True]
    after = [r for r in elig if (r.get("published_at") or "") >= GA]
    reup = [r for r in elig if r["reuploads"] and not rolling(r)]
    with_digest = [r for r in elig if r.get("first_digest")]
    verifiable = [r for r in elig if checkable(r)]
    nothing = [r for r in elig if not checkable(r)]
    before = [r for r in elig if (r.get("published_at") or "") < GA]
    orgs = [r for r in elig if r.get("owner_type") == "Organization"]
    users = [r for r in elig if r.get("owner_type") == "User"]
    dl_total = sum(r.get("download_count_latest", 0) for r in elig)
    dl_mut = sum(r.get("download_count_latest", 0) for r in elig if r["immutable"] is not True)
    return {
        "repos": len(rows), "with_release": sum(bool(r.get("release")) for r in rows), "eligible": len(elig),
        "immutable": len(imm), "immutable_pct": pct(len(imm), len(elig)), "mutable": len(elig) - len(imm),
        "mutable_pct": pct(len(elig) - len(imm), len(elig)),
        "missing_field": sum(r["immutable"] == "missing" for r in elig),
        "released_before_ga": len(before), "rolling_tags": sum(rolling(r) for r in elig),
        "checksum_in_notes_only": sum(notes_checksum(r) and not (has_checksum_file(r) or has_signature_file(r) or r.get("attestation") or r["immutable"] is True) for r in elig),
        "released_after_ga": len(after), "immutable_after_ga": sum(r["immutable"] is True for r in after),
        "immutable_after_ga_pct": pct(sum(r["immutable"] is True for r in after), len(after)),
        "orgs": len(orgs), "orgs_immutable_pct": pct(sum(r["immutable"] is True for r in orgs), len(orgs)),
        "users": len(users), "users_immutable_pct": pct(sum(r["immutable"] is True for r in users), len(users)),
        "reuploaded": len(reup), "reuploaded_pct": pct(len(reup), len(elig)),
        "checksum": sum(bool(has_checksum_file(r)) for r in elig), "checksum_pct": pct(sum(bool(has_checksum_file(r)) for r in elig), len(elig)),
        "signature": sum(bool(has_signature_file(r)) for r in elig), "signature_pct": pct(sum(bool(has_signature_file(r)) for r in elig), len(elig)),
        "with_digest": len(with_digest), "attested": sum(bool(r.get("attestation")) for r in with_digest),
        "attested_pct": pct(sum(bool(r.get("attestation")) for r in with_digest), len(with_digest)),
        "verifiable": len(verifiable), "verifiable_pct": pct(len(verifiable), len(elig)),
        "nothing_to_check": len(nothing), "nothing_to_check_pct": pct(len(nothing), len(elig)),
        "downloads_latest_total": dl_total, "downloads_latest_mutable": dl_mut,
        "downloads_latest_mutable_pct": pct(dl_mut, dl_total),
        # Figure 2: the strongest protection each release gives, one layer per release (locked > signed or attested >
        # checksum only > nothing).
        "layer_locked": len(imm),
        "layer_signed": sum(r["immutable"] is not True and (has_signature_file(r) or bool(r.get("attestation"))) for r in elig),
        "layer_checksum": sum(r["immutable"] is not True and not (has_signature_file(r) or r.get("attestation")) and checkable(r) for r in elig),
        "layer_nothing": len(nothing),
    }


BODIES.update(json.load(open(os.path.join(RAW, "bodies.json"))))
ASSETS.update(json.load(open(os.path.join(RAW, "asset_names.json"))))  # code/fetch_assets.py
top = json.load(open(os.path.join(RAW, "top.json")))
brew = json.load(open(os.path.join(RAW, "brew.json")))
A, B = top["rows"], brew["rows"]
S = {"pulled_top": top["pulled"], "pulled_brew": brew["pulled"], "ga_date": GA,
     "top": block(A), "top100": block([r for r in A if r["rank"] <= 100]), "top500": block([r for r in A if r["rank"] <= 500]),
     "brew": block([r for r in B if r.get("repo")]), "brew_no_github": sum(1 for r in B if not r.get("repo")),
     "brew_listed": len(B)}

elig = [r for r in A if software(r)]
assert not any(r["immutable"] is True and r["reuploads"] for r in elig), "an immutable release shows a re-upload"
S["sanity"] = {"missing_field_top": sum(r["immutable"] == "missing" for r in elig),
               "immutable_with_reupload": sum(r["immutable"] is True and bool(r["reuploads"]) for r in elig),
               "content_dropped": sum(1 for r in A if r.get("release") and r.get("downloads") and not software(r))}
mut = sorted([r for r in elig if r["immutable"] is not True], key=lambda r: -r.get("download_count_latest", 0))
S["top_mutable_most_downloaded"] = [{"repo": r["repo"], "tag": r["tag"], "downloads": r["download_count_latest"],
                                     "stars": r.get("stars"), "published_at": r["published_at"][:10], "checksum": bool(has_checksum_file(r)),
                                     "signature": bool(has_signature_file(r)), "attestation": r.get("attestation"),
                                     "notes_checksum": notes_checksum(r), "checkable": checkable(r)} for r in mut[:15]]
S["top_immutable"] = sorted([r["repo"] for r in elig if r["immutable"] is True])
S["reuploads"] = sorted([{"repo": r["repo"], "tag": r["tag"], "published_at": r["published_at"],
                          "max_days_after": max(a["days_after"] for a in r["reuploads"]), "assets": len(r["reuploads"]),
                          "example": max(r["reuploads"], key=lambda a: a["days_after"])["name"]}
                         for r in elig if r["reuploads"] and not rolling(r)], key=lambda x: -x["max_days_after"])
be = [r for r in B if r.get("repo") and software(r)]
S["brew_rows"] = [{"formula": r["formula"], "rank": r["rank"], "repo": r["repo"], "immutable": r["immutable"] is True,
                   "checksum": bool(has_checksum_file(r)), "signature": bool(has_signature_file(r)), "attestation": r.get("attestation"),
                   "checkable": checkable(r)}
                  for r in sorted(be, key=lambda r: r["rank"])]
S["brew_top20_eligible"] = S["brew_rows"][:20]

os.makedirs(DATA, exist_ok=True)
json.dump(S, open(os.path.join(DATA, "summary.json"), "w"), indent=1)
for name, rows in (("repos_top.csv", A), ("repos_brew.csv", B)):
    with open(os.path.join(DATA, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "formula", "repo", "stars", "owner_type", "tag", "published_at", "immutable", "download_assets",
                    "latest_downloads", "checksum_file", "signature_file", "attestation", "reuploads_over_24h", "url"])
        for r in rows:
            w.writerow([r.get("rank"), r.get("formula", ""), r.get("repo"), r.get("stars"), r.get("owner_type"), r.get("tag"),
                        r.get("published_at"), r.get("immutable"), len(r.get("downloads") or []), r.get("download_count_latest"),
                        r.get("checksum_file"), r.get("signature_file"), r.get("attestation"), len(r.get("reuploads") or []),
                        f"https://github.com/{r['repo']}/releases/tag/{r['tag']}" if r.get("tag") else ""])
for k in ("top", "top100", "brew"):
    b = S[k]
    print(k, f"eligible {b['eligible']}  immutable {b['immutable']} ({b['immutable_pct']:.1f}%)  after-GA {b['immutable_after_ga']}/{b['released_after_ga']}"
             f"  reup {b['reuploaded']}  checksum {b['checksum_pct']:.0f}%  sig {b['signature_pct']:.0f}%  attested {b['attested']}/{b['with_digest']}"
             f"  nothing {b['nothing_to_check']} ({b['nothing_to_check_pct']:.0f}%)  mutable downloads {b['downloads_latest_mutable_pct']:.0f}%")
