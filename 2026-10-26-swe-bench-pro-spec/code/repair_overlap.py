# Which of the 731 SWE-Bench Pro tasks each repair changed, and where the two repairs overlap.
import pandas as pd, numpy as np
v1 = pd.read_parquet("../raw/v1.parquet").set_index("instance_id")
v2 = pd.read_parquet("../raw/v2.parquet").set_index("instance_id")
pv = pd.read_json("../raw/pv.jsonl", lines=True).set_index("instance_id")
print("ids v1", len(v1), "v2", len(v2), "pv", len(pv), "v2 subset of v1:", set(v2.index) <= set(v1.index), "pv == v1 ids:", set(pv.index) == set(v1.index))
F = ["problem_statement", "requirements", "interface", "patch", "test_patch", "fail_to_pass", "pass_to_pass", "before_repo_set_cmd", "selected_test_files_to_run", "base_commit"]
import ast, json
def norm(x):
    if isinstance(x, (list, np.ndarray)): return json.dumps(sorted(str(e).strip() for e in x))
    x = str(x)
    t = x.strip()
    if t.startswith("["):
        try: return json.dumps(sorted(str(e).strip() for e in json.loads(t)))
        except Exception:
            try: return json.dumps(sorted(str(e).strip() for e in ast.literal_eval(t)))
            except Exception: pass
    return chr(10).join(l.strip() for l in t.splitlines() if l.strip())
def changed(a, b):
    return {f for f in F if f in a and f in b and norm(a[f]) != norm(b[f])}
dropped = set(v1.index) - set(v2.index)
sc = {i: changed(v1.loc[i], v2.loc[i]) for i in v2.index}
oc = {i: changed(v1.loc[i], pv.loc[i]) for i in pv.index}
S = {i for i, c in sc.items() if c}; O = {i for i, c in oc.items() if c}
print("Scale: dropped", len(dropped), "changed", len(S), "untouched", len(v2) - len(S))
print("OpenCompass: changed", len(O))
from collections import Counter
print("Scale fields changed:", Counter(f for c in sc.values() for f in c).most_common())
print("OC fields changed:", Counter(f for c in oc.values() for f in c).most_common())
print("OC changed & Scale dropped", len(O & dropped), "| OC changed & Scale changed", len(O & S), "| OC changed & Scale untouched", len(O - S - dropped))
print("hard flag count", int(v2.hard.sum()), "version values", v2.version.value_counts().to_dict())
