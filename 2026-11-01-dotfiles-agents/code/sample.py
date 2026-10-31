# The sample, fixed before the run: a uniform random 6,000 of all_repos.json, seed 2026.
import json, random
d = json.load(open("all_repos.json", encoding="utf-8"))
d.sort(key=lambda r: r["full_name"].lower())
s = random.Random(2026).sample(d, 6000)
json.dump(s, open("sample_6000.json", "w", encoding="utf-8"))
print(len(s), len({r["full_name"] for r in s}))
