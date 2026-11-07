import json,urllib.request,urllib.parse,concurrent.futures as cf,re,tarfile,io,os,sys
res=json.load(open('npm_probe.json'))
cand=[(n,i) for n,i in res if i and 'err' not in i]
def get(u):
    with urllib.request.urlopen(u,timeout=60) as r: return r.read()
pat=re.compile(r"""(\.claude(?:\.json|/settings|/hooks|/commands|/skills|/agents|['"/])|claude_desktop_config|\.codex/|codex.config\.toml|\.cursor/|mcp\.json|\.gemini/|windsurf|\.vscode/mcp)""",re.I)
def one(item):
    n,inst=item
    try:
        d=json.loads(get("https://registry.npmjs.org/"+urllib.parse.quote(n,safe='@')))
        v=d['versions'][d['dist-tags']['latest']]
        tb=get(v['dist']['tarball'])
        t=tarfile.open(fileobj=io.BytesIO(tb))
        files={m.name.split('/',1)[1]:m for m in t.getmembers() if m.isfile()}
        cmd=" ".join(inst.values())
        refs=set(re.findall(r"[\w./-]+\.(?:c?js|mjs|sh|cjs)",cmd))
        hits={}
        for r in refs:
            r=r.lstrip('./')
            if r in files:
                txt=t.extractfile(files[r]).read().decode('utf8','ignore')
                m=set(x.lower() for x in pat.findall(txt))
                if m: hits[r]=sorted(m)
        m=set(x.lower() for x in pat.findall(cmd))
        if m: hits['<cmd>']=sorted(m)
        return n,hits,len(refs)
    except Exception as e: return n,{'err':str(e)[:80]},0
out=[]
with cf.ThreadPoolExecutor(12) as ex:
    for r in ex.map(one,cand): out.append(r)
json.dump(out,open('npm_probe2.json','w'))
hit=[o for o in out if o[1] and 'err' not in o[1]]
print("candidates",len(cand),"hits",len(hit),"errors",sum(1 for o in out if 'err' in o[1]))
for o in hit: print(o[0],json.dumps(o[1])[:220])
