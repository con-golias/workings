# python code/which_fixes.py 2.1.300   (your version: claude --version)
import collections, json, sys

E = [e for e in json.load(open("data/entries_public.json")) if e["date"].startswith("2026")]
key = lambda v: tuple(int(x) for x in v.split("."))
mine = sys.argv[1]
later = [e for e in E if key(e["version"]) > key(mine)]
print(f"Claude Code {mine}: {len(later)} of the {len(E)} counted 2026 entries shipped in a later version.")
for check, n in collections.Counter(e["control"] for e in later).most_common():
    print(f"  {check:<20}{n:>4}")
