"""Parse every Form D primary_doc.xml into one row per filing: ../data/filings.jsonl."""
import json, os, re, xml.etree.ElementTree as ET
H = {json.loads(l)["adsh"]: json.loads(l) for l in open("../data/hits.jsonl")}
def tx(e, path):
    x = e.find(path)
    return x.text.strip() if x is not None and x.text else None
def num(v):
    try: return float(v)
    except Exception: return None
out = []
for adsh, h in H.items():
    p = "../data/xml/%s.xml" % adsh
    if not os.path.exists(p): continue
    try: r = ET.parse(p).getroot()
    except ET.ParseError: continue
    od = r.find("offeringData")
    if od is None: continue
    rel = [" ".join(filter(None, [tx(x, "relatedPersonName/firstName"), tx(x, "relatedPersonName/lastName")])) for x in r.findall("relatedPersonsList/relatedPersonInfo")]
    comp = [tx(x, "recipientName") for x in od.findall("salesCompensationList/recipient")]
    out.append({**h,
        "entity": tx(r, "primaryIssuer/entityName"), "entity_type": tx(r, "primaryIssuer/entityType"),
        "jurisdiction": tx(r, "primaryIssuer/jurisdictionOfInc"), "year_inc": tx(r, "primaryIssuer/yearOfInc/value"),
        "industry": tx(od, "industryGroup/industryGroupType"), "fund_type": tx(od, "industryGroup/investmentFundInfo/investmentFundType"),
        "amendment": tx(od, "typeOfFiling/newOrAmendment/isAmendment"), "first_sale": tx(od, "typeOfFiling/dateOfFirstSale/value"),
        "exemptions": [x.text for x in od.findall("federalExemptionsExclusions/item")],
        "min_investment": num(tx(od, "minimumInvestmentAccepted")),
        "offering_amount": tx(od, "offeringSalesAmounts/totalOfferingAmount"), "amount_sold": num(tx(od, "offeringSalesAmounts/totalAmountSold")),
        "investors": num(tx(od, "investors/totalNumberAlreadyInvested")), "non_accredited": tx(od, "investors/hasNonAccreditedInvestors"),
        "n_non_accredited": num(tx(od, "investors/numberNonAccreditedInvestors")),
        "sales_commissions": num(tx(od, "salesCommissionsFindersFees/salesCommissions/dollarAmount")),
        "finders_fees": num(tx(od, "salesCommissionsFindersFees/findersFees/dollarAmount")),
        "fees_clarification": tx(od, "salesCommissionsFindersFees/clarificationOfResponse"),
        "proceeds_to_insiders": num(tx(od, "useOfProceeds/grossProceedsUsed/dollarAmount")),
        "proceeds_clarification": tx(od, "useOfProceeds/clarificationOfResponse"),
        "sales_compensation": comp, "related": rel, "signature_date": tx(r, "offeringData/signatureBlock/signature/signatureDate")})
json.dump(out, open("../data/filings.json", "w"), indent=0)
print(len(out), "parsed")
import collections
print(collections.Counter(r["industry"] for r in out).most_common(6))
print(collections.Counter(r["fund_type"] for r in out).most_common(6))
