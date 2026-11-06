"""The hand-verified set: companies whose periodic report says an AI agent (or agentic system) may itself take an
action that is wrong, unintended, unauthorised or outside its scope. Each candidate passage was read by hand,
with its paragraph (5 Nov 2026).
Groups: a parent and its subsidiaries / co-registrants count once. Output ../data/rogue_verified.json + shared-wording links."""
import json, re, collections
# (group, name pattern as it appears in EDGAR, first date seen, form)
V = [("Tenable","Tenable Holdings","2025-11-04"),("Klaviyo","Klaviyo","2025-11-05"),("Navan","Navan, Inc","2025-12-15"),
("ITT","ITT INC","2026-02-09"),("Barclays","BARCLAYS PLC","2026-02-10"),("HubSpot","HUBSPOT","2026-02-11"),
("Prudential Financial","PRUDENTIAL FINANCIAL","2026-02-12"),("DraftKings","DraftKings","2026-02-13"),("Rush Street Interactive","Rush Street","2026-02-18"),
("GoDaddy","GoDaddy","2026-02-25"),("MercadoLibre","MERCADOLIBRE","2026-02-25"),("Bank of America","BANK OF AMERICA","2026-02-25"),
("Murphy Oil","MURPHY OIL","2026-02-25"),("Wix","Wix.com","2026-03-05"),("Fiverr","Fiverr","2026-03-12"),("DocuSign","DOCUSIGN","2026-03-18"),
("Sprinklr","Sprinklr","2026-03-19"),("ServiceTitan","ServiceTitan","2026-03-25"),("Roblox","Roblox","2026-04-30"),("Twilio","TWILIO","2026-05-01"),
("RingCentral","RingCentral","2026-05-11"),("Dynatrace","Dynatrace","2026-05-20"),("Gen Digital","Gen Digital","2026-05-21"),("Zscaler","Zscaler","2026-05-26"),
("Global AI","Global AI, Inc","2026-05-28"),("VIDA Global","VIDA Global","2026-06-26"),("Varonis","VARONIS","2026-07-29"),("Bandwidth","Bandwidth","2026-07-29"),
("Meta","Meta Platforms","2026-07-30"),("Regeneron","REGENERON","2026-07-30"),("Solowin","Solowin","2026-08-03"),("Snap","Snap Inc","2026-08-04"),
("Arvinas","ARVINAS","2026-08-04"),("Block","Block, Inc","2026-08-05"),("SUI Group","SUI Group","2026-08-06"),("Western Digital","WESTERN DIGITAL","2026-08-14"),
("Sandisk","Sandisk","2026-08-17"),("Cisco","CISCO SYSTEMS","2026-09-02"),("Samsara","Samsara","2026-09-08"),("Nutanix","Nutanix","2026-09-18"),
("Microsoft","MICROSOFT CORP","2026-10-28"),("Robinhood","Robinhood Markets","2026-10-28"),("Rimini Street","Rimini Street","2026-10-29"),
("Alphabet","Alphabet Inc","2026-10-29"),("Apple","Apple Inc","2026-11-03"),("Palantir","Palantir","2026-11-03"),("Arista","Arista Networks","2026-11-04"),
("Fastly","Fastly","2026-11-04"),("Oportun","Oportun","2026-11-04"),("CS Disco","CS Disco","2026-11-04"),("Amplitude","Amplitude","2026-11-05"),("Pattern Group","Pattern Group","2026-11-05")]
EXCLUDED = {"Riskified": "fear is customers disputing agent purchases, not the agent acting", "Palo Alto Networks": "product description",
            "Figma": "fear is agents replacing interfaces", "Salesforce, ServiceNow, Workday, UiPath, Adobe": "no such sentence (checked by reading)",
            "Pre-2025 phrase hits (Sirius XM, WEX, ICICI, Bitfarms, SEI, House of Doge)": "'agents' means employees or contractors"}
R = [json.loads(l) for l in open("../data/sentences.jsonl", encoding="utf8")]
E = json.load(open("../data/rogue_efts.json", encoding="utf8"))
def words(s): return re.findall(r"[a-z0-9]+", s.lower().replace("artificial intelligence", "ai").replace("unauthorised", "unauthorized"))
out = []
for g, pat, d in V:
    texts = [r["s"] + " " + r.get("next", "") for r in R if pat.lower() in r["name"].lower() and r["date"] == d]
    texts += [e["window"] for e in E if pat.lower() in e["name"].lower() and e["date"] == d]
    meta = next((r for r in R if pat.lower() in r["name"].lower() and r["date"] == d), None) or next(e for e in E if pat.lower() in e["name"].lower() and e["date"] == d)
    out.append({"group": g, "edgar_name": meta["name"], "first_date": d, "form": meta["form"], "text": " ".join(texts)})
K = 8
for o in out: o["sh"] = {" ".join(w[i:i+K]) for w in [words(o["text"])] for i in range(len(w) - K + 1)}
for i, o in enumerate(out):
    best = None
    for p in out[:i]:
        if p["first_date"] >= o["first_date"]: continue
        n = len(o["sh"] & p["sh"])
        if n >= 3 and (best is None or n > best[1]): best = (p["group"], n)
    o["shares_wording_with_earlier"] = best[0] if best else None
    o["shared_8grams"] = best[1] if best else 0
for o in out: del o["sh"]
json.dump({"criterion": __doc__, "verified": out, "excluded": EXCLUDED}, open("../data/rogue_verified.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(out), "companies;", sum(1 for o in out if o["shares_wording_with_earlier"]), "share >=3 eight-word runs with an earlier filer")
for o in out: print(o["first_date"], o["group"], "<-", o["shares_wording_with_earlier"], o["shared_8grams"])
