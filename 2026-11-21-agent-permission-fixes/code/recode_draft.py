# Proposes a control + precondition per entry for hand review; the reviewed result is written into
# data/entries_coded.json (source of truth) by code/apply_codes.py.
import json, re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
E = json.load(open(os.path.join(D, "entries_base.json"), encoding="utf-8"))  # frozen 271-entry list; ids below index it
C = [("policy_admin", r"OTEL|telemetry|tracing|login|forceLogin|proxy and CA|\bCA\b settings|TLS trust|availableModels|blocked model|gateway"),
     ("policy", r"managed|organi[sz]ation|\borg\b|enterprise|polic|allowManaged|admin"),
     ("hook", r"\bhook"), ("plan_mode", r"plan mode|unapproved plan|plan files|plan approval"),
     ("trust_consent", r"\btrust|consent|disclaimer|untrusted"),
     ("sandbox", r"sandbox|isolation|worktree-isolation"),
     ("deny_ask_rule", r"\bdeny\b|deny rule|ask rule|\bask\b (permission )?rules?|denyRead|denyWrite|deniedDomains|disallowedTools|Read\(|Edit\(|permission rules"),
     ("containment", r"symlink|outside (the|their|its|what)|containment|path-traversal|junction|link swapped|escape|NT `|UNC|network paths|/\.vol"),
     ("prompt", r".")]
LOOS = re.compile(r"auto[- ]mode|\bauto\b mode|in auto|auto and|bypass ?permissions|bypassPermissions|bypass mode|accept-?edits|acceptEdits|allow rules?\b|auto-allow|autoAllow|allowed-tools|dangerously-skip|skip-permissions|don't ask again|Bash\([a-z]+[:*]", re.I)
for e in E:
    e["control"] = next(k for k, p in C if re.search(p, e["text"], re.I))
    e["pre"] = "loosened" if LOOS.search(e["text"]) else "none"
json.dump(E, open(os.path.join(D, "entries_draft.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for k, _ in C:
    g = [e for e in E if e["control"] == k]
    print(f"## {k} {len(g)}")
    for i, e in enumerate(E):
        if e["control"] == k: print(i, e["pre"][0], "P" if e["platform"] else " ", e["text"][:105])
