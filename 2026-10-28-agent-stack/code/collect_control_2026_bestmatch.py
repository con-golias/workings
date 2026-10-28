# Repositories created 1-24 Oct 2026 (TS/JS, best-match order): the main 2026 sample. Output: $RAW/ctlbm_repos.json
#   RAW=raw python3 code/collect_control_2026_bestmatch.py
import json,subprocess,time,os,sys,urllib.request
import os; OUT=os.environ.get('RAW', 'raw'); os.makedirs(OUT, exist_ok=True)
def gh(args):
    for attempt in range(6):
        r=subprocess.run(['gh','api','-X','GET']+args,capture_output=True,text=True,encoding='utf-8',errors='replace')
        if r.returncode==0: return json.loads(r.stdout)
        if 'rate limit' in r.stdout+r.stderr: time.sleep(60*(attempt+1)); continue
        return None
    return None
def save(name,obj): json.dump(obj,open(f'{OUT}/{name}','w',encoding='utf-8'))
def load(name,default):
    p=f'{OUT}/{name}'
    return json.load(open(p,encoding='utf-8')) if os.path.exists(p) else default
# Repos created on each day, TS/JS, via repo search (default order)
days=[f'2026-10-{d:02d}' for d in range(1,25)]
ctl=load('ctlbm_repos.json',{})
for day in days:
    if any(v.get('day')==day for v in ctl.values()): continue
    for lang in ('TypeScript','JavaScript'):
        for page in range(1,4):
            j=gh(['search/repositories','-f',f'q=created:{day} language:{lang} fork:false','-f','per_page=100','-f',f'page={page}'])
            time.sleep(2.5)
            if not j or not j.get('items'): break
            for it in j['items']: ctl.setdefault(it['full_name'],{'day':day,'created':it['created_at'],'lang':lang})
    save('ctlbm_repos.json',ctl); print('ctl',day,len(ctl),flush=True)
print('done')
