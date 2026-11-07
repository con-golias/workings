"""Per flagged package: the write calls that sit within 12 lines of an agent-config path, plus guard lines, for reading."""
import json, re, sys, tarfile
SH = json.load(open("../data/sheet.json")); SC = json.load(open("../data/scan.json"))
exec(re.search(r"(PATH = re\.compile\(.*?re\.I\))", open("scan.py", encoding="utf8").read(), re.S).group(1))
WR = re.compile(r"writeFile|appendFile|copyFile|cpSync|\bcp\(|symlink|mkdir|createWriteStream|outputFile|writeJson|\bcp -|\bln -s|>>|\btee\b|rename", re.I)
GU = re.compile(r"npm_config_global|process\.env\.CI\b|isTTY|readline|prompt|confirm|SKIP|DISABLE|OPT_?IN|OPT_?OUT|--yes|INIT_CWD", re.I)
lo, hi = int(sys.argv[1]), int(sys.argv[2])
for r in SH[lo:hi]:
    n = r["name"]; v = SC[n]; t = tarfile.open("../data/tarballs/" + n.replace("/", "__") + ".tgz")
    files = {m.name.split("/", 1)[1] if "/" in m.name else m.name: m for m in t.getmembers() if m.isfile()}
    print("\n## [%d] %s | %s/wk | %s" % (SH.index(r), n, r["downloads"], r["description"][:90]))
    for f in v["files_read"]:
        L = t.extractfile(files[f]).read().decode("utf8", "ignore").splitlines()
        if len(L) < 5 and sum(map(len, L)) > 5000:
            print("  ", f, "[minified/bundled]"); continue
        P = [i for i, l in enumerate(L) if PATH.search(l)]
        wr = [i for i, l in enumerate(L) if WR.search(l) and any(abs(i - p) <= 12 for p in P)]
        gu = [i for i, l in enumerate(L) if GU.search(l)][:4]
        if not P: continue
        print("   %s: path@%s" % (f, [p + 1 for p in P[:5]]))
        for i in P[:3]: print("     P%4d %s" % (i + 1, L[i].strip()[:150]))
        for i in wr[:4]: print("     W%4d %s" % (i + 1, L[i].strip()[:150]))
        for i in gu: print("     G%4d %s" % (i + 1, L[i].strip()[:150]))
