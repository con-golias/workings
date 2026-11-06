"""For each pair of verified filers where reading showed the later one reusing the earlier one's agent-risk wording,
record the longest run of identical words between the two passages (sentence naming the agent + the two after it)."""
import json, re
from difflib import SequenceMatcher
d = {o["group"]: o for o in json.load(open("../data/rogue_verified.json", encoding="utf8"))["verified"]}
PAIRS = [("Klaviyo","HubSpot"),("DraftKings","Rush Street Interactive"),("GoDaddy","Wix"),("Wix","Fiverr"),("DocuSign","RingCentral"),
         ("ServiceTitan","Dynatrace"),("Dynatrace","Nutanix"),("Barclays","Gen Digital"),("Twilio","Bandwidth"),("Bandwidth","Pattern Group"),
         ("Global AI","SUI Group"),("Western Digital","Sandisk"),("Samsara","Arista")]
AGT = re.compile(r"agent|agentic|autonom|unintended|unauthori|scope|human (intervention|oversight)|actions", re.I)
def toks(s): return re.findall(r"[^\s—–]+", s)
def norm(t): return re.sub(r"[^a-z0-9]", "", t.lower().replace("unauthorised", "unauthorized"))
out = []
for a, b in PAIRS:
    ta, tb = toks(d[a]["text"]), toks(d[b]["text"])
    na, nb = [norm(x) for x in ta], [norm(x) for x in tb]
    sm = SequenceMatcher(None, nb, na, autojunk=False)
    blocks = [m for m in sm.get_matching_blocks() if m.size >= 6 and AGT.search(" ".join(tb[m.a:m.a+m.size]))]
    m = max(blocks, key=lambda m: m.size)
    out.append({"earlier": a, "earlier_date": d[a]["first_date"], "later": b, "later_date": d[b]["first_date"], "longest_identical_words": m.size,
                "run": " ".join(tb[m.a:m.a+m.size])})
    print(a, "->", b, m.size, "|", out[-1]["run"][:200])
json.dump(out, open("../data/copy_links.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
