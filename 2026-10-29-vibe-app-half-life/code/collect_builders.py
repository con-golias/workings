# Copied from the working run of 28 Oct 2026. Usage: RAW=raw python3 code/collect_builders.py [args]
import os as _os; _R = _os.environ.get("RAW", "raw"); _os.makedirs(_R, exist_ok=True); _os.chdir(_R)  # all files live in $RAW
# Census of builder-exported repos created 1-24 Oct 2025 (README text search, all pages per day).
import json,subprocess,time,os
def gh(args):
    for a in range(6):
        r=subprocess.run(['gh','api','-X','GET']+args,capture_output=True,text=True,encoding='utf-8',errors='replace')
        if r.returncode==0: return json.loads(r.stdout)
        if 'rate limit' in r.stdout+r.stderr: time.sleep(60*(a+1)); continue
        time.sleep(10)
    return None
G={'lovable':'"Lovable project" in:readme','aistudio':'"AI Studio app" in:readme','v0':'v0.dev in:readme','bolt':'bolt.new in:readme'}
p='census_repos.json'; out=json.load(open(p)) if os.path.exists(p) else {}
p2='census_counts.json'; cnt=json.load(open(p2)) if os.path.exists(p2) else {}
for d in range(1,25):
    day=f'2025-10-{d:02d}'
    for g,q in G.items():
        key=f'{g}|{day}'
        if key in cnt: continue
        total=None
        for page in range(1,11):
            j=gh(['search/repositories','-f',f'q={q} created:{day} fork:false','-f','per_page=100','-f',f'page={page}'])
            time.sleep(2.2)
            if not j: break
            total=j.get('total_count'); items=j.get('items',[])
            for it in items: out.setdefault(it['full_name'],{'g':g,'day':day,'id':it['id']})
            if len(items)<100: break
        cnt[key]=total
    json.dump(out,open(p,'w')); json.dump(cnt,open(p2,'w')); print(day,len(out),flush=True)
print('done',len(out))
