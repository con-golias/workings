# Claude Code sample (commits co-signed "Co-Authored-By: Claude", 1-24 Oct 2026) and the "recently updated" 2026 sample.
#   RAW=raw python3 code/collect_claude_and_control_2026.py   -> $RAW/agent_repos.json, $RAW/ctl_repos.json
# Agent-built vs other new JS/TS repos, Oct 2026: which npm packages do they pick?
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
# 1. agent repos: commits with Claude trailer, day by day (search returns max 1000 per query)
agent=load('agent_repos.json',{})
days=[f'2026-10-{d:02d}' for d in range(1,25)]
for day in days:
    if any(v.get('day')==day for v in agent.values()): continue
    for page in range(1,11):
        j=gh(['search/commits','-f',f'q="Co-Authored-By: Claude" committer-date:{day}','-f','per_page=100','-f',f'page={page}'])
        time.sleep(2.5)
        if not j or not j.get('items'): break
        for it in j['items']:
            fn=it['repository']['full_name']
            agent.setdefault(fn,{'day':day,'fork':it['repository'].get('fork')})
        if len(j['items'])<100: break
    save('agent_repos.json',agent); print(day,len(agent),flush=True)
# 2. control: repos created in Oct 2026, JS/TS, via repo search by day
ctl=load('ctl_repos.json',{})
for day in days:
    if any(v.get('day')==day for v in ctl.values()): continue
    for lang in ('TypeScript','JavaScript'):
        for page in range(1,4):
            j=gh(['search/repositories','-f',f'q=created:{day} language:{lang} fork:false','-f','per_page=100','-f',f'page={page}','-f','sort=updated'])
            time.sleep(2.5)
            if not j or not j.get('items'): break
            for it in j['items']: ctl.setdefault(it['full_name'],{'day':day,'created':it['created_at'],'lang':lang})
    save('ctl_repos.json',ctl); print('ctl',day,len(ctl),flush=True)
print('done')
