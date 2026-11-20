# Classifies every pulled Copyright Office record and writes data/summary.json + data/registrations.csv.
# A record counts only if an AI phrase sits in what the applicant SAID about authorship: the "material excluded"
# statement, the "material included" (new material) statement, or an author's authorship statement. A match in a
# title, a name or a note does not count (books about AI, companies called "AI Something").
#   RAW=<dir of full records> python3 code/analysis.py
import collections, csv, json, os, re, statistics

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, "..")
RAW = os.environ.get("RAW", os.path.join(root, "data", "raw"))
DEN = json.load(open(os.path.join(root, "data", "denominator.json")))

AI = re.compile(r"\bA\.?I\b\.?|artificial[ -]intelligence|machine[ -]generated|"
                r"midjourney|chat ?gpt|\bgpt-?\d|suno|\budio\b|dall[- ]?e|stable diffusion|leonardo\.?ai|firefly|"
                r"\bsora\b|runway|elevenlabs|eleven labs|\bclaude\b|\bgemini\b|copilot|\bllm\b|large language model", re.I)
TOOLS = [("Suno", r"suno"), ("ChatGPT / OpenAI GPT", r"chat ?gpt|\bgpt-?\d|openai"), ("Midjourney", r"midjourney"),
         ("DALL-E", r"dall[- ]?e"), ("Udio", r"\budio\b"), ("Stable Diffusion", r"stable diffusion"),
         ("Adobe Firefly", r"firefly"), ("Leonardo", r"leonardo"), ("ElevenLabs", r"eleven ?labs"),
         ("Runway", r"runway"), ("Sora", r"\bsora\b"), ("Claude", r"\bclaude\b"), ("Gemini", r"\bgemini\b"),
         ("Copilot", r"copilot")]
# What the AI made, read from the AI-bearing pieces of the "material excluded" statement.
PARTS = [("images", r"image|artwork|art work|\bart\b|illustrat|picture|photo|graphic|drawing|cover|visual|painting|2-d|3-d"),
         ("text", r"\btext|writ|story|prose|chapter|poem|content of the book|manuscript"),
         ("lyrics", r"lyric"),
         ("music", r"music|instrument|melod|beat|composition|track|song|sound recording|audio|vocal|voice|\bsing"),
         ("narration / voice", r"narrat|voice-?over|voiceover|spoken|speech"),
         ("video", r"video|footage|animation|motion|film|clip|scene"),
         ("code", r"\bcode\b|program|software|source code")]
COUNTRY = re.compile(r"(?:Domicile|Citizenship):\s*([^;.]+)")


def rec(path):
    d = json.load(open(path, encoding="utf-8"))
    r = (d.get("data") or [{}])[0]
    return r.get("hit", r)


def ai_bits(s):
    # pieces of a statement, split on commas / semicolons / full stops / " and ", that carry an AI phrase
    out = []
    for piece in re.split(r"[;,]|\.\s|\band\b|&", s or ""):
        if AI.search(piece):
            out.append(piece.strip())
    return out


def parts_of(stmt):
    bits = ai_bits(stmt)
    found = set()
    for b in bits:
        for name, pat in PARTS:
            if re.search(pat, b, re.I):
                found.add(name)
    # "AI-generated images and text" splits into "AI-generated images" + "text": look one piece ahead too
    m = re.search(r"(?:AI|artificial intelligence)[- ]generated ([^;.]+)", stmt or "", re.I)
    if m:
        for name, pat in PARTS:
            if re.search(pat, m.group(1), re.I):
                found.add(name)
    if "lyrics" in found and "music" in found and not re.search(r"music|instrument|melod|beat|vocal|voice|sing|audio|sound", " ".join(bits), re.I):
        found.discard("music")
    return found


kept, dropped = [], collections.Counter()
for f in sorted(os.listdir(RAW)):
    r = rec(os.path.join(RAW, f))
    if not r or r.get("type_of_record") != "registration":
        dropped["not a registration"] += 1
        continue
    ex = r.get("material_excluded_statement") or ""
    inc = " ".join(x.get("material_included_statement", "") for x in r.get("material_included_list") or [])
    auth = " ".join(x.get("author_authorship_statement", "") for x in r.get("author_statement_list") or [])
    where = [k for k, s in (("excluded", ex), ("included", inc), ("authorship", auth)) if AI.search(s)]
    if not where:
        dropped["AI only in title, name or note"] += 1
        continue
    claimants = [c.get("claimant_full_name", "").strip().rstrip(",.;") for c in r.get("claimants_list") or []]
    authors = r.get("author_statement_list") or []
    countries = set()
    for a in authors:
        for k in ("author_domicile_statement", "author_citizenship_statement"):
            m = COUNTRY.search(a.get(k) or "")
            if m:
                countries.add(m.group(1).strip())
    org = any(re.search(r"\b(LLC|Inc|Corporation|Corp|Ltd|Limited|GmbH|Company|Co\b|LLP|PBC|Studios?|Media|Publishing|Records|Group)\b", c) for c in claimants)
    allstmt = " ".join((ex, inc, auth))
    kept.append({
        "registration_number": r.get("registration_number"),
        "registration_date": r.get("registration_date") or "",
        "type_of_work": r.get("type_of_work_to_english"),
        "registration_class": (r.get("registration_number") or "")[:2],
        "claimant": "; ".join(claimants),
        "claimant_is_organization": org,
        "countries": "; ".join(sorted(countries)),
        "ai_in": "+".join(where),
        "excluded_statement": ex,
        "ai_parts": "+".join(sorted(parts_of(ex))) if "excluded" in where else "",
        "tools": "+".join(n for n, p in TOOLS if re.search(p, allstmt, re.I)),
        "human_claim": inc,
        "title": r.get("title_concatenated") or "",
    })

S = {"records_read": len(os.listdir(RAW)), "kept": len(kept), "dropped": dict(dropped)}
S["dropped_title_only"] = dropped["AI only in title, name or note"]
S["not_registration"] = dropped["not a registration"]
S["registrations_read"] = S["records_read"] - S["not_registration"]
S["kept_excluded"] = sum("excluded" in k["ai_in"] for k in kept)
S["kept_excluded_pct"] = round(100 * S["kept_excluded"] / len(kept), 1)

# by month and year, and as a share of all registrations in the same months (same catalogue, same lag)
bym = collections.Counter(k["registration_date"][:7] for k in kept if k["registration_date"])
S["first_month"] = min(bym)
S["by_month"] = {m: {"ai": bym.get(m, 0), "total": DEN[m]["total"], "per_10k": round(1e4 * bym.get(m, 0) / DEN[m]["total"], 2) if DEN[m]["total"] else None} for m in sorted(DEN)}
S["by_year"] = {}
for y in ("2022", "2023", "2024", "2025", "2026"):
    a = sum(v for m, v in bym.items() if m.startswith(y))
    t = sum(DEN[m]["total"] for m in DEN if m.startswith(y))
    S["by_year"][y] = {"ai": a, "total": t, "per_10k": round(1e4 * a / t, 2), "one_in": round(t / a) if a else None}
# a month counts as complete if the catalogue holds at least 80% of 2025's median month (records arrive late)
MED25 = statistics.median(DEN[f"2025-{m:02d}"]["total"] for m in range(1, 13))
S["by_quarter"] = []
for y in range(2023, 2027):
    for q in range(4):
        ms = [f"{y}-{m:02d}" for m in range(3 * q + 1, 3 * q + 4)]
        if any(m not in DEN for m in ms):
            continue
        a = sum(bym.get(m, 0) for m in ms)
        t = sum(DEN[m]["total"] for m in ms)
        full = all(DEN[m]["total"] >= 0.8 * MED25 for m in ms)
        S["by_quarter"].append({"q": f"{y} Q{q + 1}", "ai": a, "total": t, "per_10k": round(1e4 * a / t, 1), "complete": full})
QC = [q for q in S["by_quarter"] if q["complete"]]
S["last_full_quarter_label"] = QC[-1]["q"]
S["first_q"], S["last_q"] = QC[0], QC[-1]
S["first_q_one_in"], S["last_q_one_in"] = round(1e4 / QC[0]["per_10k"]), round(1e4 / QC[-1]["per_10k"])
S["rise_x"] = round(QC[-1]["per_10k"] / QC[0]["per_10k"], 1)
S["incomplete_from"] = min(m for m in DEN if DEN[m]["total"] < 0.8 * MED25 and m >= "2026-01")
pre = sum(v for m, v in bym.items() if m < "2022")
S["before_2022"] = pre

# type of work, 2025 + 2026 to date, vs all registrations of that type
TW = {"Text": "text", "Music": "music", "Visual Material": "visual_material", "Motion Pictures": "motion_picture",
      "Sound Recording and Music": "sound_recording_music", "Computer Files": "computer_file", "Sound Recording": "sound_recording",
      "Dramatic Works; or Choreography": "dramatic_work_choreography"}
recent = [k for k in kept if k["registration_date"] >= "2025-01-01"]
S["recent_n"] = len(recent)
S["recent_total"] = sum(DEN[m]["total"] for m in DEN if m >= "2025-01")
S["recent_per_10k"] = round(1e4 * len(recent) / S["recent_total"], 1)
S["recent_one_in"] = round(S["recent_total"] / len(recent))
tw = collections.Counter(k["type_of_work"] for k in recent)
S["by_type"] = []
for name, key in TW.items():
    tot = sum(DEN[m]["type_of_work"].get(key, 0) for m in DEN if m >= "2025-01")
    S["by_type"].append({"type": name, "ai": tw.get(name, 0), "total": tot, "per_10k": round(1e4 * tw.get(name, 0) / tot, 1) if tot else None})
S["by_type"].sort(key=lambda x: -x["per_10k"])
S["by_type_map"] = {x["type"]: x for x in S["by_type"]}
S["music_all"] = sum(tw.get(n, 0) for n in ("Music", "Sound Recording and Music", "Sound Recording"))
S["text_recent"] = tw.get("Text", 0)

# what the AI made
ex = [k for k in kept if k["ai_parts"] or "excluded" in k["ai_in"]]
pc = collections.Counter(p for k in ex for p in (k["ai_parts"].split("+") if k["ai_parts"] else ["not said"]))
S["parts_n"] = len(ex)
S["parts"] = {p: {"n": n, "pct": round(100 * n / len(ex), 1)} for p, n in pc.most_common()}
books = [k for k in kept if k["type_of_work"] == "Text" and "excluded" in k["ai_in"]]
bi = sum(1 for k in books if "images" in k["ai_parts"] and "text" not in k["ai_parts"])
bt = sum(1 for k in books if "text" in k["ai_parts"])
S["books"] = {"n": len(books), "images_only": bi, "images_only_pct": round(100 * bi / len(books), 1), "text": bt, "text_pct": round(100 * bt / len(books), 1)}
songs = [k for k in kept if k["type_of_work"] in ("Music", "Sound Recording and Music", "Sound Recording") and "excluded" in k["ai_in"]]
sc = collections.Counter()
for k in songs:
    p = set(k["ai_parts"].split("+")) if k["ai_parts"] else set()
    sc["music"] += "music" in p
    sc["lyrics"] += "lyrics" in p
    sc["lyrics_not_music"] += "lyrics" in p and "music" not in p
    sc["music_not_lyrics"] += "music" in p and "lyrics" not in p
sc["human_lyrics"] = sum(1 for k in songs if re.search(r"lyric", k["human_claim"], re.I))
S["songs"] = {"n": len(songs), "human_lyrics_pct": round(100 * sc["human_lyrics"] / len(songs), 1), **{k: v for k, v in sc.items()}, "music_pct": round(100 * sc["music"] / len(songs), 1), "music_not_lyrics_pct": round(100 * sc["music_not_lyrics"] / len(songs), 1), "lyrics_pct": round(100 * sc["lyrics"] / len(songs), 1)}
# precautionary disclaimers: "Material (if any) generated by AI", "some material may be generated by AI"
HEDGE = re.compile(r"\(if any\)|\bif any\b|may (?:have been|be|contain)[^.;]{0,40}(?:\bAI\b|artificial)|possibly|potentially|to the extent", re.I)
hed = [k for k in kept if HEDGE.search(k["excluded_statement"])]
hed_org = [k for k in hed if k["claimant_is_organization"]]
S["hedged"] = {"n": len(hed), "orgs": collections.Counter(re.sub(r"[,.]", "", k["claimant"].split("; ")[0]).strip() for k in hed_org).most_common(6),
               "org_share": round(100 * sum(k["claimant_is_organization"] for k in hed) / max(1, len(hed)), 1)}
# one literary agency and the AI-written books
AGENCY = [k for k in books if "Lukeman" in k["claimant"]]
S["agency"] = {"n": len(AGENCY), "text": sum("text" in k["ai_parts"] for k in AGENCY)}
S["agency"]["share_of_book_text"] = round(100 * S["agency"]["text"] / max(1, S["books"]["text"]), 1)
rest = [k for k in books if "Lukeman" not in k["claimant"]]
S["books_without_agency"] = {"n": len(rest), "text_pct": round(100 * sum("text" in k["ai_parts"] for k in rest) / len(rest), 1),
                             "images_only_pct": round(100 * sum("images" in k["ai_parts"] and "text" not in k["ai_parts"] for k in rest) / len(rest), 1)}
code = [k for k in kept if "code" in k["ai_parts"]]
S["code"] = {"n": len(code), "orgs": collections.Counter(k["claimant"] for k in code if k["claimant_is_organization"]).most_common(8)}

# tools named
tc = collections.Counter(t for k in kept for t in (k["tools"].split("+") if k["tools"] else []))
S["tools_any"] = sum(1 for k in kept if k["tools"])
S["tools_any_pct"] = round(100 * S["tools_any"] / len(kept), 1)
S["tools"] = tc.most_common()

# who files
cc = collections.Counter()
for k in kept:
    for c in k["claimant"].split("; "):
        c2 = re.sub(r"[,.]", "", c).strip()
        if c2:
            cc[c2] += 1
S["claimants_unique"] = len(cc)
S["top_claimants"] = [(c, n) for c, n in cc.most_common(60) if re.search(r"\b(LLC|Inc|Corporation|Corp|Ltd|Limited|GmbH|Company|LLP|PBC|Studios?|Media|Publishing|Records|Group|Management|Productions?|Scout|Entertainment)\b", c, re.I)][:25]  # organisations only
S["top10_share"] = round(100 * sum(n for _, n in cc.most_common(10)) / len(kept), 1)
S["single_filers"] = sum(1 for n in cc.values() if n == 1)
S["single_filers_pct"] = round(100 * S["single_filers"] / len(cc), 1)
ORG = re.compile(r"\b(LLC|Inc|Corporation|Corp|Ltd|Limited|GmbH|Company|LLP|PBC|Studios?|Media|Publishing|Records|Group|Management|Productions?|Scout|Entertainment)\b", re.I)
S["top_orgs"] = [(c, n) for c, n in cc.most_common() if ORG.search(c)][:12]
# private individuals are counted, never named
S["top_individual_counts"] = [n for c, n in cc.most_common() if not ORG.search(c)][:5]
S["top_org_share"] = round(100 * S["top_orgs"][0][1] / len(kept), 1)
S["filers_5plus"] = sum(1 for n in cc.values() if n >= 5)
# the single biggest filer, and the software category without it
TOP = next(c for c, n in S["top_orgs"] if c.startswith("Pluralsight"))  # the online-course company that dominates computer files
mine = [k for k in kept if re.sub(r"[,.]", "", k["claimant"]).strip() == TOP]
S["pluralsight"] = S["top_org"] = {"name": TOP, "n": len(mine), "types": collections.Counter(k["type_of_work"] for k in mine).most_common(),
                "parts": collections.Counter(p for k in mine for p in (k["ai_parts"].split("+") if k["ai_parts"] else ["not said"])).most_common()}
cf_all = S["by_type_map"]["Computer Files"]
cf_top = sum(1 for k in mine if k["type_of_work"] == "Computer Files" and k["registration_date"] >= "2025-01-01")
S["computer_files_without_top"] = {"ai": cf_all["ai"] - cf_top, "total": cf_all["total"] - cf_top,
                                   "per_10k": round(1e4 * (cf_all["ai"] - cf_top) / (cf_all["total"] - cf_top), 1), "top_n": cf_top}
S["org_share"] = round(100 * sum(k["claimant_is_organization"] for k in kept) / len(kept), 1)
co = collections.Counter(c for k in kept for c in (k["countries"].split("; ") if k["countries"] else []))
S["countries"] = co.most_common(15)
S["with_country"] = sum(1 for k in kept if k["countries"])
S["non_us"] = sum(1 for k in kept if k["countries"] and k["countries"] != "United States")
S["non_us_pct"] = round(100 * S["non_us"] / S["with_country"], 1)

# cross-check against the Office's own public figure (Law360, 21 Apr 2026: "more than 6,000")
S["kept_excluded_by_2026_04_21"] = sum(1 for k in kept if "excluded" in k["ai_in"] and k["registration_date"] and k["registration_date"] <= "2026-04-21")
S["kept_by_2026_04_21"] = sum(1 for k in kept if k["registration_date"] and k["registration_date"] <= "2026-04-21")
S["vs_office"] = "higher" if S["kept_by_2026_04_21"] > 6000 else "lower"
# second public figure: "more than 7,000" reported from the Register's Senate testimony of 12 May 2026 (secondary reports)
S["kept_by_2026_05_12"] = sum(1 for k in kept if k["registration_date"] and k["registration_date"] <= "2026-05-12")
S["kept_excluded_by_2026_05_12"] = sum(1 for k in kept if "excluded" in k["ai_in"] and k["registration_date"] and k["registration_date"] <= "2026-05-12")
S["dropped_title_pct"] = round(100 * S["dropped_title_only"] / S["records_read"], 1)
S["books_share_of_text_ai"] = round(100 * S["books"]["n"] / max(1, sum(1 for k in kept if k["type_of_work"] == "Text")), 1)
def disp(c):
    c = re.sub(r"[,.]?\s*(Inc|LLC|Ltd|Limited|Corporation|Corp|CO\.?,?\s*Limited)\.?$", "", c.strip(), flags=re.I).strip(" ,.")
    return {"International Business Machines": "IBM"}.get(c, c)


S["code"]["orgs_display"] = [(disp(c), n) for c, n in S["code"]["orgs"]]
S["top_orgs_display"] = [(disp(c), n) for c, n in S["top_orgs"]]
S["hedged"]["orgs_display"] = [(disp(c), n) for c, n in S["hedged"]["orgs"]]
# token-safe aliases (render.py paths cannot hold spaces)
safe = lambda x: re.sub(r"[^a-z0-9]+", "_", x.lower()).strip("_")
S["bt"] = {safe(x["type"]): x for x in S["by_type"]}
S["pp"] = {safe(k): v for k, v in S["parts"].items()}
S["tool"] = {safe(n): c for n, c in S["tools"]}
json.dump(S, open(os.path.join(root, "data", "summary.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
with open(os.path.join(root, "data", "registrations.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(kept[0]))
    w.writeheader()
    # private individuals are not named in the public data either: organisations keep their name as claimant, and a
    # person's name inside any statement ("written by Jane Doe", "Text spoken by Jane Doe") becomes "[name]"
    NAME = re.compile(r"\b((?:by|written by|spoken by|edited by|narrated by|voiced by)\s+)(?!Artificial\b)[A-Z][a-z]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z]+)+")
    scrub = lambda t: NAME.sub(lambda m: m.group(1) + "[name]", t or "")
    w.writerows(sorted(({**k, "claimant": k["claimant"] if k["claimant_is_organization"] else "(individual)",
                         "excluded_statement": scrub(k["excluded_statement"]), "human_claim": scrub(k["human_claim"])} for k in kept),
                       key=lambda k: k["registration_date"] or ""))
print(json.dumps({k: S[k] for k in ("records_read", "kept", "dropped", "kept_excluded_pct", "recent_n", "recent_per_10k", "recent_one_in", "parts", "books", "songs", "tools_any_pct", "top10_share", "org_share", "non_us_pct")}, indent=1))
print(S["by_year"]); print(S["by_type"]); print(S["tools"][:10]); print(S["top_claimants"][:15]); print(S["countries"][:10]); print(S["code"])
