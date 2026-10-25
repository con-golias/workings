# The remaining counts quoted in the article: the Hard subset against the rest, and how long the requirements are.
# Run spec_coverage.py first (it writes ../data/spec_strict_per_task.csv).
import pandas as pd
v1 = pd.read_parquet("../raw/v1.parquet").set_index("instance_id")
v2 = pd.read_parquet("../raw/v2.parquet").set_index("instance_id")
R = pd.read_csv("../data/spec_strict_per_task.csv")
a = R[(R.ver == "pro_v2") & (R.n_ids > 0)].copy()
a["hard"] = a.id.map(v2.hard).astype(bool)
for h, g in a.groupby("hard"):
    print("V2", "Hard" if h else "rest", "| tasks needing new names", len(g), "| names in prompt %", round(100 * g.ids_full.sum() / g.n_ids.sum(), 1))
def text(s): return s.astype(str).str.replace(r"\n", "\n", regex=False)  # v1 stores line breaks as the two characters \n
for name, d in (("v1", v1), ("V2", v2)):
    req, issue = text(d.requirements), text(d.problem_statement)
    bullets = req.map(lambda t: sum(1 for l in t.splitlines() if l.strip().lstrip('"').startswith("-")))
    print(name, "| median requirement bullets", bullets.median(), "| requirements longer than issue %", round(100 * (req.str.len() > issue.str.len()).mean(), 1))
