# Copied from the working run of 28 Oct 2026. Usage: RAW=raw python3 code/fetch_activity.py [args]
import os as _os; _R = _os.environ.get("RAW", "raw"); _os.makedirs(_R, exist_ok=True); _os.chdir(_R)  # all files live in $RAW
# Commit activity (latest 100 commits: date, author email/login), homepage and README for a list of repos.
import json,subprocess,sys,os,time
src,dst=sys.argv[1],sys.argv[2]
R=json.load(open(src)); R=list(R) if isinstance(R,dict) else R
out=json.load(open(dst)) if os.path.exists(dst) else {}
todo=[r for r in R if r not in out]
F='''createdAt pushedAt homepageUrl isFork isArchived primaryLanguage{name}
readme:object(expression:"HEAD:README.md"){... on Blob{text}}
pkg:object(expression:"HEAD:package.json"){... on Blob{byteSize}}
defaultBranchRef{target{... on Commit{history(first:30){totalCount nodes{committedDate author{email name user{login}}}}}}}'''
for i in range(0,len(todo),25):
    ch=todo[i:i+25]
    q='query{'+' '.join(f'r{k}:repository(owner:{json.dumps(r.split("/")[0])},name:{json.dumps(r.split("/",1)[1])}){{{F}}}' for k,r in enumerate(ch))+'}'
    for a in range(5):
        x=subprocess.run(['gh','api','graphql','-f',f'query={q}'],capture_output=True,text=True,encoding='utf-8',errors='replace')
        try: d=json.loads(x.stdout)
        except Exception: d={}
        if d.get('data'): break
        time.sleep(20*(a+1))
    for k,r in enumerate(ch):
        y=(d.get('data') or {}).get(f'r{k}')
        if not y: out[r]=None; continue
        h=((y.get('defaultBranchRef') or {}).get('target') or {}).get('history') or {'totalCount':0,'nodes':[]}
        out[r]=dict(created=y['createdAt'],pushed=y['pushedAt'],home=y['homepageUrl'],fork=y['isFork'],archived=y['isArchived'],
                    lang=(y.get('primaryLanguage') or {}).get('name'),pkg=bool(y.get('pkg')),total=h['totalCount'],
                    readme=((y.get('readme') or {}).get('text') or '')[:3000],
                    commits=[(n['committedDate'],(n['author'] or {}).get('email') or '',((n['author'] or {}).get('user') or {}).get('login') or '',(n['author'] or {}).get('name') or '') for n in h['nodes']])
    if i%400==0: json.dump(out,open(dst,'w')); print(i,len(out),flush=True)
json.dump(out,open(dst,'w')); print('done',len(out))
