"""Candidates for the 'an agent may act on its own' risk: an agent sentence (or one of the two after it) that uses an
action phrase. Every candidate is then read by hand; the verdicts live in ../data/rogue_verified.json."""
import json, re, collections
R = [json.loads(l) for l in open("../data/sentences.jsonl", encoding="utf8")]
ACT = re.compile(r"unintended or unauthori[sz]ed|unauthori[sz]ed (autonomous )?(actions?|transactions?)|outside (the )?scope of (their|its)|exceed\w* (their |its |the )?(permissions|authori)|overstep|irreversib|conceal|resist\w* instructions|defy\w* (instructions|directions)|disregard\w* instructions|actions? that (are|were) not (directed|instructed|authori)|pursue unintended|take (harmful|unintended|erroneous|incorrect) actions|actions? .{0,40}(erroneous|irreversible|misaligned)|without (human )?(supervision|oversight)|beyond (their|its) (intended )?scope|outside (of )?(their|its) intended scope|act outside approved", re.I)
best = collections.OrderedDict()
for r in sorted(R, key=lambda r: r["date"]):
    for part in (r["s"], r.get("next", "")):
        m = ACT.search(part)
        if m and r["cik"] not in best:
            best[r["cik"]] = {"name": r["name"], "date": r["date"], "form": r["form"], "adsh": r["adsh"], "file": r["file"],
                              "agent_sentence": r["s"], "match_in": "same" if part is r["s"] else "next", "text": part[:900], "match": m.group(0)}
json.dump(list(best.values()), open("../data/rogue_candidates.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(best))
for i, b in enumerate(best.values()):
    print("\n[%d] %s | %s %s | %s | match: %s" % (i, b["name"][:45], b["date"], b["form"], b["match_in"], b["match"]))
    if b["match_in"] == "next": print("   AGENT:", b["agent_sentence"][:250])
    print("   TEXT:", b["text"][:600])
