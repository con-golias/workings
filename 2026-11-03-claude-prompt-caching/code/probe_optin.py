import os,re,collections
SRC=('.py','.ts','.tsx','.js','.mjs','.cjs','.jsx')
SKIP=('node_modules','/dist/','/build/','.venv','venv/','/.next/','site-packages')
CC=re.compile(r'cache_control|cacheControl|ephemeral')
AGSDK=re.compile(r'claude_agent_sdk|claude-agent-sdk|@anthropic-ai/claude-agent-sdk|claude_code_sdk|@anthropic-ai/claude-code')
DIRECT=re.compile(r'messages\.create\(|messages\.stream\(|ChatAnthropic|@ai-sdk/anthropic|anthropic\(|/v1/messages|createAnthropic|AnthropicVertex|AnthropicBedrock|litellm')
TOOLS=re.compile(r'tool_use|tool_result|"tools"\s*:|\btools\s*=|\btools\s*:')
rows=[]
for repo in sorted(os.listdir('repos')):
    t=''
    for root,_,files in os.walk(os.path.join('repos',repo)):
        if any(s in root+'/' for s in SKIP) or '/.git' in root: continue
        for f in files:
            if f.endswith(SRC):
                try: t+=open(os.path.join(root,f),errors='ignore').read()+'\n'
                except: pass
    rows.append(dict(repo=repo,cc=bool(CC.search(t)),agsdk=bool(AGSDK.search(t)),direct=bool(DIRECT.search(t)),tools=bool(TOOLS.search(t))))
c=collections.Counter()
for r in rows:
    if r['agsdk'] and not r['direct']: c['agent_sdk_only']+=1; continue
    if not r['direct']: c['no_direct_call_found']+=1; continue
    k=('tools' if r['tools'] else 'notools')+'_'+('cache' if r['cc'] else 'nocache'); c[k]+=1
print(len(rows),dict(c))
