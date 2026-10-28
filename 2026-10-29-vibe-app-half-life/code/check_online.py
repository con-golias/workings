# Copied from the working run of 28 Oct 2026. Usage: RAW=raw python3 code/check_online.py [args]
import os as _os; _R = _os.environ.get("RAW", "raw"); _os.makedirs(_R, exist_ok=True); _os.chdir(_R)  # all files live in $RAW
import json,urllib.request,concurrent.futures as cf,ssl
U=json.load(open('urls.json')); out={}
ctx=ssl.create_default_context()
def check(u):
    try:
        req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (research; con_golias)'})
        with urllib.request.urlopen(req,timeout=20,context=ctx) as r:
            body=r.read(4000).decode('utf-8','replace'); return r.status,body[:300]
    except urllib.error.HTTPError as e:
        try: body=e.read(1000).decode('utf-8','replace')
        except Exception: body=''
        return e.code,body[:300]
    except Exception as e:
        return 0,str(e)[:120]
jobs=[(g,r,u) for g,L in U.items() for r,u in L]
with cf.ThreadPoolExecutor(24) as ex:
    for (g,r,u),res in zip(jobs,ex.map(lambda j:check(j[2]),jobs)):
        out[r]={'g':g,'url':u,'status':res[0],'body':res[1]}
json.dump(out,open('online.json','w')); print('done',len(out))
