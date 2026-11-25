# Applies the hand review (20 Nov 2026) to the drafted codes and writes them, keyed by text, into
# data/entries_coded.json, which is from now on the single source of truth. Run once after recode_draft.py.
# control: which control the fix is about. pre: "none" = default use, "loosened" = only after the user loosened it.
import json, os, re
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
E = json.load(open(os.path.join(D, "entries_draft.json"), encoding="utf-8"))
CTRL = {16: "deny_ask_rule", 50: "sandbox", 119: "containment", 150: "trust_consent", 235: "trust_consent",
        269: "sandbox", 231: "deny_ask_rule", 264: "deny_ask_rule", 3: "injection", 34: "injection", 36: "injection",
        51: "prompt", 218: "prompt", 6: "deny_ask_rule", 26: "prompt", 28: "prompt", 14: "prompt", 31: "containment",
        104: "containment", 143: "deny_ask_rule", 139: "deny_ask_rule", 142: "deny_ask_rule", 263: "prompt",
        9: "policy", 18: "hook", 172: "deny_ask_rule", 182: "plan_mode", 188: "sandbox", 261: "prompt",
        106: "trust_consent", 72: "trust_consent", 179: "trust_consent", 242: "containment", 233: "policy",
        5: "prompt", 27: "prompt", 117: "deny_ask_rule", 46: "plan_mode", 70: "plan_mode",
        # second review (20 Nov): the sandbox cell must mean "the sandbox itself failed"
        42: "prompt", 170: "deny_ask_rule", 171: "deny_ask_rule", 178: "prompt", 53: "containment", 85: "containment",
        94: "containment", 24: "prompt", 76: "prompt", 25: "prompt", 87: "trust_consent", 38: "prompt",
        15: "prompt"}
PRE = {59: "none", 67: "none", 32: "none", 155: "none", 157: "none", 227: "none", 26: "none", 28: "none",
       55: "none", 70: "none", 38: "none", 5: "loosened", 117: "loosened", 182: "loosened", 46: "loosened",
       261: "loosened", 142: "loosened", 139: "loosened", 14: "loosened",
       # sandbox auto-allow was the default once the sandbox was on until 2.1.325 ("Changed sandboxed Bash commands to
       # follow the normal permission flow by default"), so these are not the user loosening anything
       6: "sandbox_auto_allow", 42: "sandbox_auto_allow", 170: "sandbox_auto_allow", 171: "sandbox_auto_allow",
       178: "sandbox_auto_allow", 136: "none", 122: "none", 37: "none"}
NOT_PLATFORM = {76}
for i, e in enumerate(E):
    e["control"] = CTRL.get(i, e["control"]); e["pre"] = PRE.get(i, e["pre"])
    if i in NOT_PLATFORM: e["platform"] = False
    # 2.1.259 Read() deny rules on Bash arguments: reverted in 2.1.260 for over-blocking; kept in the count, footnoted
    e["reverted"] = e["version"] == "2.1.259" and e["text"].startswith("Fixed Bash `Read()` deny rules not covering files given as option values")
    e.pop("bucket", None); e.pop("id", None)
# Auto mode has been the built-in default since 2.1.228 (macOS, Linux, WSL) per the permission-modes docs read 21 Nov
# (data/doc_permission_modes.md), and in terminal sessions from 2.1.283. An entry that names auto mode, shipped in
# 2.1.228 or later, is not "the user loosened something": precondition "auto_default". The 2.1.323 entry about an
# explicit --permission-mode auto / defaultMode setting stays "loosened".
# Read in full by hand, 21 Nov: the ten loosened entries from 2.1.228 on that name auto mode. Rule: when auto mode
# alone is enough for the gap (other modes may be named too), precondition "auto_default". When the gap also needs an
# approval the user had saved (2.1.285 "approved that artifact earlier", 2.1.296 "a saved permission allows"), it
# stays "loosened", as does 2.1.323 (an explicit --permission-mode auto / defaultMode setting).
AUTO_DEFAULT = {"2.1.257", "2.1.271", "2.1.280", "2.1.281", "2.1.290", "2.1.292", "2.1.316", "2.1.319"}
for e in E:
    if e["pre"] == "loosened" and e["version"] in AUTO_DEFAULT and "auto" in e["text"].lower()             and not e["text"].startswith("Fixed `--permission-mode auto`"):
        e["pre"] = "auto_default"
# precision check (40 random + 4 unclear-direction lines, 20 Nov): 43 hold; this one is cut because the direction is
# unclear (going back to an earlier mode may be stricter or looser)
E = [e for e in E if not (e["version"] == "2.1.325" and e["text"].startswith("Fixed a session sometimes going back to an earlier permission mode"))]
json.dump(E, open(os.path.join(D, "entries_coded.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(E))
