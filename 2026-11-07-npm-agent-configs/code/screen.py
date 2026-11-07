"""Which packages' latest version runs code at install time? Abbreviated packuments carry hasInstallScript; the
version document carries the scripts and the tarball URL. Output ../data/install_scripts.json."""
import json, urllib.request, urllib.parse, concurrent.futures as cf, sys, time
U = json.load(open("../data/universe.json"))
def get(url, accept=None):
    for i in range(4):
        try:
            h = {"User-Agent": "workings-research"}
            if accept: h["Accept"] = accept
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r: return json.loads(r.read())
        except Exception as e:
            if getattr(e, "code", 0) == 404: return None
            time.sleep(2 * (i + 1))
    return None
def one(n):
    a = get("https://registry.npmjs.org/" + urllib.parse.quote(n, safe="@"), "application/vnd.npm.install-v1+json")
    if not a or "dist-tags" not in a: return n, None
    v = a["dist-tags"].get("latest"); ver = a["versions"].get(v, {})
    if not ver.get("hasInstallScript"): return n, {"version": v, "install": False}
    full = get("https://registry.npmjs.org/%s/%s" % (urllib.parse.quote(n, safe="@"), v))
    sc = (full or {}).get("scripts", {})
    return n, {"version": v, "install": True, "scripts": {k: sc[k] for k in ("preinstall", "install", "postinstall") if k in sc},
               "tarball": (full or {}).get("dist", {}).get("tarball"), "description": (full or {}).get("description", "")[:200]}
out = {}
with cf.ThreadPoolExecutor(24) as ex:
    for i, (n, r) in enumerate(ex.map(one, list(U))):
        out[n] = dict(r or {"missing": True}, sets=U[n]["sets"])
        if i % 2000 == 0: print(i, file=sys.stderr)
json.dump(out, open("../data/install_scripts.json", "w"))
A = [n for n in out if any(s.startswith("A:") for s in out[n]["sets"])]; B = [n for n in out if "B:high-impact" in out[n]["sets"]]
for lab, S in (("A agent", A), ("B high-impact", B)):
    print(lab, len(S), "with install script:", sum(1 for n in S if out[n].get("install")), "missing:", sum(1 for n in S if out[n].get("missing")))
