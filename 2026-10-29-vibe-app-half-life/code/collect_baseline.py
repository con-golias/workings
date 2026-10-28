# Copied from the working run of 28 Oct 2026. Usage: RAW=raw python3 code/collect_baseline.py [args]
import os as _os; _R = _os.environ.get("RAW", "raw"); _os.makedirs(_R, exist_ok=True); _os.chdir(_R)  # all files live in $RAW
# Unbiased baseline: random pages of GET /repositories?since=<id> inside the ID range of repos created 1-24 Oct 2025.
import json,subprocess,random,os,time
LO,HI=1067495000,1082897000
random.seed(20251001)
p='base_pages.json'; pages=json.load(open(p)) if os.path.exists(p) else {}
starts=sorted(random.sample(range(LO,HI),400))
for s in starts:
    if str(s) in pages: continue
    for a in range(5):
        r=subprocess.run(['gh','api',f'repositories?since={s}','--jq','[.[] | {id, full_name, fork}]'],capture_output=True,text=True,encoding='utf-8',errors='replace')
        if r.returncode==0: break
        time.sleep(30*(a+1))
    try: pages[str(s)]=json.loads(r.stdout)
    except Exception: pages[str(s)]=[]
    if len(pages)%50==0: json.dump(pages,open(p,'w')); print(len(pages),flush=True)
json.dump(pages,open(p,'w'))
repos={x['full_name']:{'id':x['id'],'page':s} for s,L in pages.items() for x in L if not x['fork']}
json.dump(repos,open('base_repos.json','w')); print('repos',len(repos))
# stage 1: light metadata
F='createdAt isFork primaryLanguage{name} pkg:object(expression:"HEAD:package.json"){... on Blob{text}}'
R=list(repos); meta={}
for i in range(0,len(R),40):
    ch=R[i:i+40]
    q='query{'+' '.join(f'r{k}:repository(owner:{json.dumps(r.split("/")[0])},name:{json.dumps(r.split("/",1)[1])}){{{F}}}' for k,r in enumerate(ch))+'}'
    for a in range(4):
        x=subprocess.run(['gh','api','graphql','-f',f'query={q}'],capture_output=True,text=True,encoding='utf-8',errors='replace')
        try: d=json.loads(x.stdout)
        except Exception: d={}
        if d.get('data'): break
        time.sleep(20*(a+1))
    for k,r in enumerate(ch):
        y=(d.get('data') or {}).get(f'r{k}')
        if not y: meta[r]=None; continue
        txt=(y.get('pkg') or {}).get('text')
        meta[r]=dict(created=y['createdAt'],lang=(y.get('primaryLanguage') or {}).get('name'),pkg=txt[:60000] if txt else None)
    if i%2000==0: json.dump(meta,open('base_meta.json','w')); print('meta',i,flush=True)
json.dump(meta,open('base_meta.json','w')); print('done')
