"""Shared HTTP helper for SEC endpoints: polite User-Agent, <=8 requests/second, retries."""
import json, os, time, urllib.request, urllib.parse, threading
# The SEC asks for a User-Agent with a contact: set SEC_UA="Your Name your@email" before running.
UA = os.environ.get("SEC_UA", "independent research your@email")
_lock = threading.Lock(); _last = [0.0]
def get(url, raw=False, tries=5):
    for i in range(tries):
        with _lock:
            wait = 0.125 - (time.time() - _last[0])
            if wait > 0: time.sleep(wait)
            _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
            return b if raw else json.loads(b)
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2 * (i + 1))
def efts(q, forms, start, end, frm=0):
    u = ("https://efts.sec.gov/LATEST/search-index?q=%s&forms=%s&dateRange=custom&startdt=%s&enddt=%s&from=%d"
         % (urllib.parse.quote(q), urllib.parse.quote(forms, safe=","), start, end, frm))
    return get(u)
