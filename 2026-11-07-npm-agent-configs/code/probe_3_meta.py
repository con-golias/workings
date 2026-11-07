import json,urllib.request,urllib.parse,re,tarfile,io,os,concurrent.futures as cf
out=json.load(open('npm_probe2.json'))
hit=[o for o in out if o[1] and 'err' not in o[1]]
def get(u):
    with urllib.request.urlopen(u,timeout=60) as r: return r.read()
os.makedirs('tars',exist_ok=True)
def one(o):
    n=o[0]
    d=json.loads(get("https://registry.npmjs.org/"+urllib.parse.quote(n,safe='@')))
    v=d['versions'][d['dist-tags']['latest']]
    tb=get(v['dist']['tarball'])
    fn='tars/'+n.replace('/','__')+'.tgz'; open(fn,'wb').write(tb)
    try: dl=json.loads(get("https://api.npmjs.org/downloads/point/last-week/"+n))['downloads']
    except Exception: dl=None
    return n,dl,v.get('description','')[:100],v.get('scripts',{}).get('postinstall') or v.get('scripts',{}).get('install') or v.get('scripts',{}).get('preinstall')
with cf.ThreadPoolExecutor(8) as ex: meta=list(ex.map(one,hit))
json.dump(meta,open('meta.json','w'))
for m in sorted(meta,key=lambda x:-(x[1] or 0)): print(m[1],m[0],'|',m[2])
