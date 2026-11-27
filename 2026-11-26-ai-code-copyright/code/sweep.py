# Recall check that does not depend on phrases: broad single words, restricted to Computer Files registered from
# Oct 2023, every hit pulled in full (records already pulled are skipped). Adds to data/ids.json under "sweep:<word>".
#   python code/sweep.py
import json, os, time, urllib.parse, urllib.request, concurrent.futures as cf
B = "https://api.publicrecords.copyright.gov/search_service_external/"
here = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(here, "..", "data", "raw"); OLD_RAW = os.path.join(here, "..", "..", "2026-11-11-copyright-ai-disclaimers", "data", "raw")
WORDS = ["AI", "generated", "generative", "agent", "assisted", "automated", "model", "tool", "artificial", "LLM", "copilot", "machine",
         # tool names, added 25 Nov: under the Computer Files filter the personal-name noise is small
         "Claude", "Codex", "Cursor", "Gemini", "GPT", "Anthropic", "OpenAI", "Windsurf"]
def get(u):
    for k in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "curl/8.0"}), timeout=120))
        except Exception: time.sleep(2 + 2 * k)
def ql(w):
    out, p = [], 1
    while True:
        q = {"query": w, "field_type": "keyword", "records_per_page": 100, "page_number": p, "type_of_work": "computer_file",
             "date_field": "registration_date_as_date", "start_date": "2023-10-01 00:00:00", "end_date": "2026-11-30 23:59:59"}
        d = get(B + "simple_search_dsl?" + urllib.parse.urlencode(q))
        if d is None: print("FAILED", w, p, flush=True); break
        h = d.get("data") or []; out += [x["hit"]["public_records_id"] for x in h]
        if len(h) < 100: break
        p += 1
    return w, out
P = os.path.join(here, "..", "data", "ids.json"); ids = json.load(open(P))
with cf.ThreadPoolExecutor(4) as ex:
    for w, o in ex.map(ql, WORDS):
        print(w, len(o), flush=True)
        for i in o: ids.setdefault(i, []).append("sweep:" + w)
json.dump(ids, open(P, "w"))
todo = [i for i in ids if not os.path.exists(os.path.join(OLD_RAW, i + ".json")) and not os.path.exists(os.path.join(RAW, i + ".json"))]
print("to fetch", len(todo), flush=True)
def full(i):
    d = get(B + "search_unique_record?" + urllib.parse.urlencode({"query": i}))
    if d: json.dump(d, open(os.path.join(RAW, i + ".json"), "w"))
with cf.ThreadPoolExecutor(12) as ex: list(ex.map(full, todo))
print("done", flush=True)
