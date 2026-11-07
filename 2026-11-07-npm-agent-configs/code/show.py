"""Print the code around every agent-config path in a package's install-time files (for reading by hand)."""
import json, re, sys, tarfile
SC = json.load(open("../data/scan.json")); IS = json.load(open("../data/install_scripts.json"))
PATH = re.compile(r"""\.claude\.json|\.claude[/\'"`]|claude_desktop_config|\.codex[/\'"`]|\.cursor[/\'"`]|\.gemini[/\'"`]|\.mcp\.json|windsurf|\.codeium|\.continue[/\'"`]|\.opencode|\.config/opencode|\.kiro[/\'"`]|\.amp[/\'"`]""", re.I)
W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
for n in sys.argv[1].split(","):
    v = SC[n]; t = tarfile.open("../data/tarballs/" + n.replace("/", "__") + ".tgz")
    files = {m.name.split("/", 1)[1] if "/" in m.name else m.name: m for m in t.getmembers() if m.isfile()}
    print("\n" + "=" * 100 + "\n##", n, "| scripts:", json.dumps(IS[n]["scripts"])[:200])
    for f in v["files_read"]:
        L = t.extractfile(files[f]).read().decode("utf8", "ignore").splitlines()
        if len(L) < 3 and sum(map(len, L)) > 5000: print(" --", f, "[minified]"); continue
        idx = [i for i, l in enumerate(L) if PATH.search(l)]
        if not idx: continue
        print(" --", f, len(L), "lines; first 3 lines:", " / ".join(x.strip()[:80] for x in L[:3]))
        shown = set()
        for i in idx[:6]:
            for j in range(max(0, i - W), min(len(L), i + W + 1)):
                if j not in shown: print("   %4d %s" % (j + 1, L[j][:170])); shown.add(j)
            print("   ....")
