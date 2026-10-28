# GraphQL: createdAt, primary language, root markers and package.json for a list of repos (50 per query)
import json,subprocess,sys,os,time
src,dst=sys.argv[1],sys.argv[2]
repos=list(json.load(open(src,encoding='utf-8')).keys())
out=json.load(open(dst,encoding='utf-8')) if os.path.exists(dst) else {}
todo=[r for r in repos if r not in out]
F='''nameWithOwner createdAt isFork stargazerCount primaryLanguage{name}
pkg:object(expression:"HEAD:package.json"){... on Blob{text byteSize}}
root:object(expression:"HEAD:"){... on Tree{entries{name type}}}'''
for i in range(0,len(todo),40):
    chunk=todo[i:i+40]
    parts=[]
    for k,r in enumerate(chunk):
        o,n=r.split('/',1)
        parts.append(f'r{k}:repository(owner:{json.dumps(o)},name:{json.dumps(n)}){{{F}}}')
    q='query{'+' '.join(parts)+' rateLimit{remaining cost}}'
    for att in range(5):
        p=subprocess.run(['gh','api','graphql','-f',f'query={q}'],capture_output=True,text=True,encoding='utf-8',errors='replace')
        try: d=json.loads(p.stdout)
        except Exception: d={}
        if d.get('data'): break
        time.sleep(20*(att+1))
    data=(d or {}).get('data') or {}
    for k,r in enumerate(chunk):
        x=data.get(f'r{k}')
        if not x: out[r]=None; continue
        txt=(x.get('pkg') or {}).get('text')
        out[r]=dict(created=x['createdAt'],fork=x['isFork'],stars=x['stargazerCount'],lang=(x.get('primaryLanguage') or {}).get('name'),
                    pkg=txt[:200000] if txt else None,root=[e['name'] for e in ((x.get('root') or {}).get('entries') or [])])
    if i%400==0:
        json.dump(out,open(dst,'w',encoding='utf-8')); print(i,len(out),(data.get('rateLimit') or {}),flush=True)
json.dump(out,open(dst,'w',encoding='utf-8')); print('done',len(out))
