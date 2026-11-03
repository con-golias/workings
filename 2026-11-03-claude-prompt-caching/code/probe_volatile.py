import os,re,sys,collections
SRC=('.py','.ts','.tsx','.js','.mjs','.cjs','.jsx')
SKIP=('node_modules','/dist/','/build/','.venv','venv/','/.next/','site-packages')
CC=re.compile(r'cache_control|cacheControl|prompt_cache_key|ephemeral')
SYS=re.compile(r'''(\bsystem\s*[:=]|["']role["']\s*:\s*["']system["']|system_prompt|systemPrompt|SYSTEM_PROMPT)''')
TIME=re.compile(r'datetime\.(?:now|utcnow)\(\)(?!\s*\.(?:date|strftime\(\s*["\']%Y-%m-%d["\']))|time\.time\(\)|Date\.now\(\)|new Date\(\)\.(?:toISOString|toLocaleString|toString|toLocaleTimeString|getTime)\(\)|new Date\(\)(?!\.toLocaleDateString|\.toDateString)|uuid4\(\)|crypto\.randomUUID\(\)|Math\.random\(\)')
res=collections.Counter(); hits=[]
for repo in sorted(os.listdir('repos')):
    has_cc=False; vol=[]
    for root,_,files in os.walk(os.path.join('repos',repo)):
        if any(s in root+'/' for s in SKIP) or '/.git' in root: continue
        for f in files:
            if not f.endswith(SRC): continue
            p=os.path.join(root,f)
            try: L=open(p,errors='ignore').read().splitlines()
            except: continue
            txt='\n'.join(L)
            if CC.search(txt): has_cc=True
            for i,l in enumerate(L):
                if SYS.search(l):
                    win=L[max(0,i-6):i+7]
                    for w in win:
                        if TIME.search(w): vol.append((p,i+1,w.strip()[:140])); break
    res['repos']+=1
    if has_cc: res['uses_cache_marker']+=1
    if vol: res['volatile_near_system']+=1; hits.append((repo,has_cc,vol[:3]))
print(res)
for h in hits: print(h[0],'CC' if h[1] else '--'); [print('   ',x[0].split('/',2)[-1][:70],x[1],'|',x[2]) for x in h[2]]
