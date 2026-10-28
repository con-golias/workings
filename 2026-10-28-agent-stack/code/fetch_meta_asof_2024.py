# Oct 2024 repos: package.json and root entries as of 30 Nov 2024 (not today's HEAD)
import json,subprocess,sys,os,time
src,dst=sys.argv[1],sys.argv[2]
repos=list(json.load(open(src,encoding='utf-8')).keys())
out=json.load(open(dst,encoding='utf-8')) if os.path.exists(dst) else {}
todo=[r for r in repos if r not in out]
F='''nameWithOwner createdAt isFork primaryLanguage{name}
defaultBranchRef{target{... on Commit{history(first:1,until:"2024-11-30T23:59:59Z"){nodes{oid committedDate
 file(path:"package.json"){object{... on Blob{text}}} tree{entries{name}}}}}}}'''
for i in range(0,len(todo),40):
    chunk=todo[i:i+40]
    q='query{'+' '.join(f'r{k}:repository(owner:{json.dumps(r.split("/",1)[0])},name:{json.dumps(r.split("/",1)[1])}){{{F}}}' for k,r in enumerate(chunk))+'}'
    for att in range(5):
        p=subprocess.run(['gh','api','graphql','-f',f'query={q}'],capture_output=True,text=True,encoding='utf-8',errors='replace')
        try: d=json.loads(p.stdout)
        except Exception: d={}
        if d.get('data'): break
        time.sleep(20*(att+1))
    data=(d or {}).get('data') or {}
    for k,r in enumerate(chunk):
        x=data.get(f'r{k}')
        try: node=x['defaultBranchRef']['target']['history']['nodes'][0]
        except Exception: out[r]=None; continue
        txt=((node.get('file') or {}).get('object') or {}).get('text')
        out[r]=dict(created=x['createdAt'],fork=x['isFork'],lang=(x.get('primaryLanguage') or {}).get('name'),asof=node['committedDate'],
                    pkg=txt[:200000] if txt else None,root=[e['name'] for e in ((node.get('tree') or {}).get('entries') or [])])
    if i%400==0: json.dump(out,open(dst,'w',encoding='utf-8')); print(i,len(out),flush=True)
json.dump(out,open(dst,'w',encoding='utf-8')); print('done',len(out))
