import json,urllib.request,urllib.parse,concurrent.futures as cf,re,sys
def get(u):
    with urllib.request.urlopen(u,timeout=30) as r: return json.load(r)
names=[]
for q in ["keywords:mcp","keywords:claude-code"]:
    for frm in range(0,1000,250):
        d=get("https://registry.npmjs.org/-/v1/search?text=%s&size=250&from=%d&popularity=1.0"%(urllib.parse.quote(q),frm))
        names+= [o['package']['name'] for o in d['objects']]
names=list(dict.fromkeys(names))
print(len(names),file=sys.stderr)
pat=re.compile(r"\.claude|claude_desktop|\.codex|codex|\.cursor|mcp\.json|settings\.json|windsurf|gemini",re.I)
def one(n):
    try:
        d=get("https://registry.npmjs.org/"+urllib.parse.quote(n,safe='@'))
        v=d['versions'][d['dist-tags']['latest']]
        s=v.get('scripts',{})
        inst={k:s[k] for k in ('preinstall','install','postinstall') if k in s}
        return n,inst
    except Exception as e: return n,{'err':str(e)[:60]}
res=[]
with cf.ThreadPoolExecutor(16) as ex:
    for n,inst in ex.map(one,names): res.append((n,inst))
json.dump(res,open('npm_probe.json','w'))
hasinst=[r for r in res if r[1] and 'err' not in r[1]]
print("total",len(res),"with install scripts",len(hasinst))
for n,i in hasinst: print(n,json.dumps(i)[:200])
