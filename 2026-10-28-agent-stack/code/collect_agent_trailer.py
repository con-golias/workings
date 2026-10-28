# Repositories with a commit co-signed by an agent, 1-24 Oct 2026, up to 1,000 commits per day.
#   RAW=raw python3 code/collect_agent_trailer.py cursor "cursoragent@cursor.com"
#   RAW=raw python3 code/collect_agent_trailer.py codex "Co-authored-by: Codex"
import json,subprocess,time,os,sys
import os; OUT=os.environ.get('RAW', 'raw'); os.makedirs(OUT, exist_ok=True); name=sys.argv[1]; phrase=sys.argv[2]
def gh(args):
    for attempt in range(6):
        r=subprocess.run(['gh','api','-X','GET']+args,capture_output=True,text=True,encoding='utf-8',errors='replace')
        if r.returncode==0: return json.loads(r.stdout)
        if 'rate limit' in r.stdout+r.stderr: time.sleep(60*(attempt+1)); continue
        return None
    return None
p=f'{OUT}/{name}_repos.json'
rep=json.load(open(p,encoding='utf-8')) if os.path.exists(p) else {}
for d in range(1,25):
    day=f'2026-10-{d:02d}'
    if any(v.get('day')==day for v in rep.values()): continue
    for page in range(1,11):
        j=gh(['search/commits','-f',f'q="{phrase}" committer-date:{day}','-f','per_page=100','-f',f'page={page}'])
        time.sleep(2.5)
        if not j or not j.get('items'): break
        for it in j['items']: rep.setdefault(it['repository']['full_name'],{'day':day,'fork':it['repository'].get('fork')})
        if len(j['items'])<100: break
    json.dump(rep,open(p,'w',encoding='utf-8')); print(name,day,len(rep),flush=True)
print('done',name,len(rep))
