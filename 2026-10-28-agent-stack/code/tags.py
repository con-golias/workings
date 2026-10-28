import json,re
def scaffold(d,v,h):
    tags=set()
    readme=(h or {}).get('readme','') if h else ''
    if {'class-variance-authority','tailwind-merge','clsx'}<=d or 'shadcn' in d or (v.get('root') and 'components.json' in v['root']): tags.add('shadcn')
    if 'next' in d and 'eslint-config-next' in d or re.search(r'create-next-app',readme,re.I): tags.add('create-next-app')
    if {'vite','@vitejs/plugin-react','eslint-plugin-react-refresh'}<=d or re.search(r'React \+ TypeScript \+ Vite|create-vite',readme,re.I): tags.add('create-vite')
    if 'turbo' in d and v.get('root') and 'turbo.json' in v['root']: tags.add('turbo')
    if 'expo' in d: tags.add('expo')
    if 'astro' in d: tags.add('astro')
    return tags
MARKERS={'CLAUDE.md':'claude','.claude':'claude','AGENTS.md':'agents','.cursorrules':'cursor','.cursor':'cursor','.github':None,'GEMINI.md':'gemini','.windsurfrules':'windsurf','.codex':'codex'}
def markers(v):
    r=set(v.get('root') or [])
    return {t for f,t in MARKERS.items() if t and f in r}
def builder(r,d,v,readme):
    import re
    rd=readme or ''
    root=set(v.get('root') or [])
    t=set()
    if 'lovable-tagger' in d or re.search(r'lovable\.dev|lovable\.app',rd,re.I): t.add('lovable')
    if re.search(r'Run and deploy your AI Studio app|ai\.studio/apps|aistudio\.google\.com/apps',rd,re.I): t.add('ai-studio')
    if re.search(r'bolt\.new',rd,re.I) or '.bolt' in root: t.add('bolt')
    if re.search(r'v0\.dev|v0\.app',rd,re.I): t.add('v0')
    if '.replit' in root or 'replit.md' in root: t.add('replit')
    if '.idx' in root or re.search(r'Firebase Studio',rd,re.I): t.add('firebase-studio')
    if '.kiro' in root: t.add('kiro')
    if '.windsurf' in root or '.windsurfrules' in root: t.add('windsurf')
    if '.trae' in root: t.add('trae')
    return t
