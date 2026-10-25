# What the agent is told vs what the hidden tests check. Strict version.
# Answer identifier: a name DEFINED on a '+' line of the gold patch, NOT present on its '-' lines (new, not a rewrite),
# called by the hidden tests, at least 5 characters, not a dunder, not a generic word.
# Expected message: a string literal of 8-80 chars containing a space, added by the fix and asserted by the hidden tests.
import re, json, pandas as pd, numpy as np
GENERIC = set("""Close close String user validate result results main email code data response parse value values message Type Delete Error
error config handler params options props state input output name type value key index item items event events errors init setup
""".split())
DEF = re.compile(r"^\+\s*(?:export\s+)?(?:async\s+)?(?:def|func(?:\s*\([^)]*\))?|class|function|type|const|let|var)\s+([A-Za-z_][A-Za-z0-9_]{4,})", re.M)
LIT = re.compile(r"""["']([^"'\n]{8,80})["']""")
def has(n, t): return re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(n), t) is not None
def lines(p, c): return "\n".join(l[1:] for l in p.splitlines() if l.startswith(c) and not l.startswith(c * 3))
def measure(df, ver, prompt_fields):
    out = []
    for i, r in df.iterrows():
        rem = lines(r.patch, "-")
        ids = {n for n in DEF.findall(r.patch) if not n.startswith("__") and n not in GENERIC and not has(n, rem) and has(n, r.test_patch)}
        lits = {s for s in LIT.findall(lines(r.test_patch, "+")) if " " in s.strip() and s in lines(r.patch, "+")}
        issue = str(r.problem_statement); full = "\n".join(str(r[f]) for f in prompt_fields)
        out.append(dict(ver=ver, id=i, repo=r.repo, n_ids=len(ids), ids_issue=sum(has(n, issue) for n in ids), ids_full=sum(has(n, full) for n in ids),
                        n_msgs=len(lits), msgs_issue=sum(s in issue for s in lits), msgs_full=sum(s in full for s in lits)))
    return pd.DataFrame(out)
v1 = pd.read_parquet("../raw/v1.parquet").set_index("instance_id")
v2 = pd.read_parquet("../raw/v2.parquet").set_index("instance_id")
vf = pd.read_parquet("../raw/verified.parquet").set_index("instance_id")
R = pd.concat([measure(vf, "verified", ["problem_statement"]),
               measure(v1, "pro_v1", ["problem_statement", "requirements", "interface"]),
               measure(v2, "pro_v2", ["problem_statement", "requirements", "interface"])])
R.to_csv("../data/spec_strict_per_task.csv", index=False)
S = []
for v, g in R.groupby("ver", sort=False):
    a = g[g.n_ids > 0]; b = g[g.n_msgs > 0]
    S.append(dict(version=v, tasks=len(g), tasks_with_new_names=len(a), new_names=int(a.n_ids.sum()),
                  names_in_issue_pct=round(100 * a.ids_issue.sum() / a.n_ids.sum(), 1), names_in_prompt_pct=round(100 * a.ids_full.sum() / a.n_ids.sum(), 1),
                  tasks_all_names_in_prompt_pct=round(100 * (a.ids_full == a.n_ids).mean(), 1),
                  tasks_with_messages=len(b), messages_in_issue_pct=round(100 * b.msgs_issue.sum() / max(1, b.n_msgs.sum()), 1),
                  messages_in_prompt_pct=round(100 * b.msgs_full.sum() / max(1, b.n_msgs.sum()), 1)))
S = pd.DataFrame(S); print(S.T.to_string()); S.to_csv("../data/spec_summary.csv", index=False)
