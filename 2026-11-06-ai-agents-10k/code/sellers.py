"""Agent talk vs agent warnings in each company's latest annual report (10-K/20-F) in the corpus.
'Agent sentences' = sentences naming AI agents, agentic AI, autonomous agents or a branded agent product (Agentforce).
'Warns' = in the hand-verified set (an agent may itself take a wrong or unauthorised action), in any report."""
import json, gzip, re
H = [json.loads(l) for l in open("../data/hits.jsonl", encoding="utf8")]
V = {o["group"] for o in json.load(open("../data/rogue_verified.json", encoding="utf8"))["verified"]}
AG = re.compile(r"\bAI[- ]agents?\b|\bartificial intelligence agents?\b|\bagentic\b|\bautonomous (?:AI )?agents?\b|\bAI-powered agents?\b|\bAgentforce\b|\bagents?\b(?=[^.]{0,80}\b(AI|autonom))", re.I)
CO = [("Salesforce", "Salesforce"), ("ServiceNow", "ServiceNow"), ("UiPath", "UiPath"), ("Workday", "Workday"), ("Adobe", "ADOBE"),
      ("Microsoft", "MICROSOFT"), ("Alphabet", "Alphabet"), ("Meta", "Meta Platforms"), ("Apple", "Apple Inc"), ("Palantir", "Palantir"), ("Twilio", "TWILIO")]
out = []
for g, pat in CO:
    hs = sorted([h for h in H if pat.lower() in h["display_names"][0].lower() and h["form"] in ("10-K", "20-F")], key=lambda h: h["file_date"])
    if not hs: out.append({"group": g, "annual": None}); continue
    h = hs[-1]; adsh, fn = h["id"].split(":", 1)
    t = gzip.open("../data/docs/%s__%s.txt.gz" % (adsh, fn.replace("/", "_")), "rt", encoding="utf8").read().replace("\n", " ")
    sents = re.split(r"(?<=[.;])\s+(?=[A-Z•])", t)
    n = sum(1 for s in sents if AG.search(s) and not re.search(r"attorneys?-in-fact|employees,? (?:and|or) agents|agents,? (?:and|or) (?:employees|contractors)|transfer agent|paying agent|registered agent|agents of the", s, re.I))
    out.append({"group": g, "annual": h["file_date"], "form": h["form"], "agent_sentences": n, "warns": g in V})
    print(g, h["file_date"], n, g in V)
json.dump(out, open("../data/sellers.json", "w", encoding="utf8"), indent=1)
