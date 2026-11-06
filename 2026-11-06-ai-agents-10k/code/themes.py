"""Tag each agent sentence that reads as a risk (a modal or a harm word) with the risks it names. Rules are plain
regexes so anyone can audit them. Company-level counts: a company names a risk if any of its filings does."""
import json, re, collections
R = [json.loads(l) for l in open("../data/sentences.jsonl")]
RISKY = re.compile(r"\b(could|may|might|risk|risks|adverse|adversely|harm|harmful|liabilit|uncertain|threat|exposure)\w*", re.I)
T = {
 "acts_unintended": r"unintended|unauthori[sz]ed (actions?|transactions?)|outside (the )?scope|exceed\w* (its|their|the)? ?(authori|permission|scope)|overstep|stray|irreversib|difficult to reverse|disregard instructions|conceal|without (human )?(supervision|oversight)|misaligned|act(s|ing)? in ways|pursue unintended",
 "security": r"cyber|attack|threat actor|prompt injection|hijack|malicious|vulnerab|breach|adversarial|hack|social engineering|reconnaissance",
 "fraud_payments": r"fraud|dispute|chargeback|erroneous payment|scam|money laundering|sanctions",
 "agents_buy_for_customers": r"on behalf of (consumers|customers|users|shoppers|travel\w*|buyers|their users)|agentic (shopping|commerce|checkout|browsing|search)|AI[- ]enabled (search|shopping)|shopping agents?|comparison[- ]shopping|disintermediat|bypass|direct (relationship|traffic|channels?)|traffic to our|book(ing)? travel|purchase products",
 "competition": r"compet",
 "demand_for_our_work": r"reduc\w* (the )?(demand|need) for|billable|headcount|replace (human|workers|employees|our)|fewer (seats|users|employees)|seat[- ]based|per[- ]seat|user[- ]based|pricing model|non-user|render obsolete|obsolete",
 "errors_quality": r"error|inaccura|hallucinat|incorrect|defect|bias|flawed",
 "legal_liability": r"liabilit|legal(ly)? responsib|indemn|litigation|lawsuit|regulat|law\b|laws\b|compliance|privacy|consent",
 "data_leak": r"confidential|proprietary information|personal data|sensitive (information|data)|disclos\w* (of )?(sensitive|confidential)",
}
WINDOW = {"acts_unintended"}  # the "such agents may..." sentence often follows the one that names the agent
T = {k: re.compile(v, re.I) for k, v in T.items()}
comp_first = collections.defaultdict(dict)  # theme -> cik -> first date
comp_any = {}
names = {}
for r in R:
    w = r["s"] + " " + r.get("next", "")
    if not RISKY.search(r["s"]): continue
    names[r["cik"]] = r["name"]
    comp_any[r["cik"]] = min(comp_any.get(r["cik"], "9"), r["date"])
    for k, p in T.items():
        if p.search(r["s"]) or (k in WINDOW and p.search(r.get("next", ""))):
            d = comp_first[k]; d[r["cik"]] = min(d.get(r["cik"], "9"), r["date"])
all_c = {r["cik"] for r in R}
print("companies with any agent sentence:", len(all_c), "| with an agent risk sentence:", len(comp_any))
for k in T:
    d = comp_first[k]
    byq = collections.Counter(v[:4] + ("H1" if v[5:7] <= "06" else "H2") for v in d.values())
    print("%-26s %4d companies (%4.1f%%) first-seen by half: %s" % (k, len(d), 100 * len(d) / len(comp_any), dict(sorted(byq.items()))))
json.dump({"n_any": len(all_c), "n_risk": len(comp_any), "themes": {k: comp_first[k] for k in T}, "risk_first": comp_any, "names": names},
          open("../data/themes.json", "w"))
