# Collects, for each repository in a list, its latest release: immutable flag, download assets, re-uploads, checksum and
# signature files, and whether the first binary asset has a GitHub attestation. Uses a logged-in gh CLI.
#   python3 code/collect.py top RAW_DIR          # list A: top 2,000 repos by stars
#   python3 code/collect.py brew RAW_DIR         # list B: Homebrew top 200 installs-on-request, GitHub upstreams
import json, os, re, subprocess, sys, time, urllib.request
from datetime import datetime, timedelta

MODE, RAW = sys.argv[1], sys.argv[2]
os.makedirs(RAW, exist_ok=True)
DL = re.compile(r"\.(exe|msi|msix|dmg|pkg|deb|rpm|apk|aab|appimage|zip|tar\.gz|tgz|tar\.xz|txz|tar\.zst|tar\.bz2|7z|jar|whl|vsix|bin|run|snap|flatpak|nupkg|gem|xpi|crx)$", re.I)
BARE = re.compile(r"(linux|darwin|macos|windows|win64|win32|freebsd)[-_.]?(amd64|x86_64|arm64|aarch64|386|x64|arm)?", re.I)
NOT_DL = re.compile(r"\.(sha256|sha512|sha1|md5|sig|asc|minisig|pem|crt|bundle|sigstore|sigstore\.json|intoto\.jsonl|txt|json|yml|yaml|xml|md|pdf|epub|png|jpg|svg|html|apkg)$", re.I)
CHECKSUM = re.compile(r"(sha256|sha512|checksum|\.sha\d+$|sums)", re.I)
SIGNATURE = re.compile(r"\.(sig|asc|minisig|pem|bundle|sigstore|sigstore\.json|intoto\.jsonl)$", re.I)


def gh(path):
    for attempt in range(4):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        if "Not Found" in r.stderr or "404" in r.stderr:
            return None
        time.sleep(5 * (attempt + 1))
    return None


def is_download(name):
    if NOT_DL.search(name):
        return False
    return bool(DL.search(name)) or ("." not in name[-6:] and bool(BARE.search(name)))


def top_repos(n=2000):
    """Top-n by stars: the search API caps at 1,000 per query, so walk down in star bands."""
    out, seen, hi = [], set(), None
    while len(out) < n:
        q = "stars:>1000" if hi is None else f"stars:1000..{hi}"
        got_any = False
        for page in range(1, 11):
            d = gh(f"search/repositories?q={q}&sort=stars&order=desc&per_page=100&page={page}")
            if not d or not d.get("items"):
                break
            for x in d["items"]:
                if x["full_name"] not in seen:
                    seen.add(x["full_name"]); got_any = True
                    out.append({"full_name": x["full_name"], "stargazers_count": x["stargazers_count"],
                                "archived": x["archived"], "owner": {"type": x["owner"]["type"]}})
                hi = x["stargazers_count"]
            time.sleep(2.2)
        if not got_any:
            break
    return out[:n]


def brew_repos(n=200):
    req = urllib.request.Request("https://formulae.brew.sh/api/analytics/install-on-request/30d.json", headers={"User-Agent": "research"})
    items = json.load(urllib.request.urlopen(req, timeout=60))["items"][:n]
    out = []
    for it in items:
        f = it["formula"]
        try:
            meta = json.load(urllib.request.urlopen(urllib.request.Request(f"https://formulae.brew.sh/api/formula/{f}.json", headers={"User-Agent": "research"}), timeout=60))
        except Exception:
            out.append({"formula": f, "rank": it["number"], "repo": None}); continue
        repo = None
        for u in [((meta.get("urls") or {}).get("stable") or {}).get("url") or "", meta.get("homepage") or ""]:
            m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", u)
            if m:
                repo = f"{m.group(1)}/{m.group(2).removesuffix('.git')}"; break
        out.append({"formula": f, "rank": it["number"], "count": it["count"], "repo": repo})
        time.sleep(0.2)
    return out


def inspect(repo, meta=None):
    rel = gh(f"repos/{repo}/releases/latest")
    if not rel or "tag_name" not in rel:
        return {"repo": repo, "release": False}
    meta = meta or gh(f"repos/{repo}") or {}  # list A passes the search metadata (saves one call per repo)
    pub = datetime.fromisoformat(rel["published_at"].replace("Z", "+00:00")) if rel.get("published_at") else None
    assets = rel.get("assets", [])
    dls = [a for a in assets if is_download(a["name"])]
    reup = [{"name": a["name"], "created_at": a["created_at"], "days_after": round((datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")) - pub).total_seconds() / 86400, 1)}
            for a in dls if pub and datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")) - pub > timedelta(hours=24)]
    att = None
    first = next((a for a in dls if a.get("digest")), None)
    if first:
        d = gh(f"repos/{repo}/attestations/{first['digest']}")
        att = bool(d and d.get("attestations"))
    return {"repo": repo, "release": True, "tag": rel["tag_name"], "published_at": rel.get("published_at"),
            "immutable": rel.get("immutable", "missing"), "owner_type": (meta.get("owner") or {}).get("type"),
            "stars": meta.get("stargazers_count"), "archived": meta.get("archived"),
            "assets": len(assets), "downloads": [a["name"] for a in dls],
            "download_count_latest": sum(a.get("download_count", 0) for a in dls),
            "checksum_file": any(CHECKSUM.search(a["name"]) for a in assets),
            "signature_file": any(SIGNATURE.search(a["name"]) for a in assets),
            "first_digest": first.get("digest") if first else None, "attestation": att, "reuploads": reup}


if MODE == "top":
    # The list is fetched once and reused (a rerun keeps the same 2,000); inspection runs on 6 threads, well under
    # GitHub's limits (one release call, at most one attestation call per repo).
    from concurrent.futures import ThreadPoolExecutor
    path = os.path.join(RAW, "top_repos.json")
    names = json.load(open(path)) if os.path.exists(path) else top_repos()
    json.dump(names, open(path, "w"))
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda im: {"rank": im[0] + 1, **inspect(im[1]["full_name"], im[1])}, enumerate(names)))
    json.dump({"pulled": datetime.utcnow().isoformat() + "Z", "rows": res}, open(os.path.join(RAW, "top.json"), "w"), indent=0)
else:
    items = brew_repos()
    rows = []
    for it in items:
        rows.append({**it, **(inspect(it["repo"]) if it["repo"] else {"release": False})})
    json.dump({"pulled": datetime.utcnow().isoformat() + "Z", "rows": rows}, open(os.path.join(RAW, "brew.json"), "w"), indent=0)
print("done", MODE)
