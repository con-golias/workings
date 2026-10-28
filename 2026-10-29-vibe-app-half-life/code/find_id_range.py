# Copied from the working run of 28 Oct 2026. Usage: RAW=raw python3 code/find_id_range.py [args]
import os as _os; _R = _os.environ.get("RAW", "raw"); _os.makedirs(_R, exist_ok=True); _os.chdir(_R)  # all files live in $RAW
import json,subprocess,sys
def created_after(since):
    r=subprocess.run(['gh','api',f'repositories?since={since}','--jq','.[0:5][] | .full_name'],capture_output=True,text=True)
    for name in r.stdout.split():
        j=subprocess.run(['gh','api',f'repos/{name}','--jq','.created_at'],capture_output=True,text=True)
        if j.returncode==0 and j.stdout.strip(): return j.stdout.strip()
    return None
def find(target, lo, hi):
    while hi-lo>20000:
        mid=(lo+hi)//2; c=created_after(mid)
        print(mid,c,flush=True)
        if c is None or c<target: lo=mid
        else: hi=mid
    return lo,hi
print('start',find('2025-10-01T00:00:00Z',1000000000,1432096027))
print('end',find('2025-10-25T00:00:00Z',1000000000,1432096027))
