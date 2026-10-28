# For new repos with a package.json: last 50 commit messages (agent trailers) and README head (scaffold notes)
import json,subprocess,sys,os,time,re
meta_f,dst=sys.argv[1],sys.argv[2]
M=json.load(open(meta_f,encoding='utf-8'))
todo=[r for r,v in M.items() if v and v.get('pkg') and v['created']>='2026-10-01']
out=json.load(open(dst,encoding='utf-8')) if os.path.exists(dst) else {}
todo=[r for r in todo if r not in out]
F='''defaultBranchRef{target{... on Commit{history(first:50){totalCount nodes{message author{email}}}}}}
readme:object(expression:"HEAD:README.md"){... on Blob{text}}'''
for i in range(0,len(todo),25):
    chunk=todo[i:i+25]
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
        if not x or not x.get('defaultBranchRef'): out[r]=None; continue
        h=x['defaultBranchRef']['target']['history']
        msgs=[n['message'] for n in h['nodes']]
        out[r]=dict(total=h['totalCount'],n=len(msgs),
          claude=sum(1 for m in msgs if re.search(r'co-authored-by:\s*claude',m,re.I)),
          cursor=sum(1 for m in msgs if 'cursoragent@cursor.com' in m.lower()),
          codex=sum(1 for m in msgs if re.search(r'co-authored-by:\s*codex',m,re.I)),
          copilot=sum(1 for m in msgs if 'copilot' in m.lower()),
          first=msgs[-1][:300] if msgs else '',readme=((x.get('readme') or {}).get('text') or '')[:1500])
    if i%250==0: json.dump(out,open(dst,'w',encoding='utf-8')); print(i,len(out),flush=True)
json.dump(out,open(dst,'w',encoding='utf-8')); print('done',len(out))
