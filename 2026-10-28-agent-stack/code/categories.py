CATS={
 'test runner':['vitest','jest','mocha','ava','@playwright/test'],
 'unit test runner':['vitest','jest','mocha','ava'],
 'bundler/dev server':['vite','webpack','parcel','esbuild','rollup','@rspack/core','tsup'],
 'linter':['eslint','@biomejs/biome','oxlint'],
 'formatter':['prettier','@biomejs/biome','oxfmt','dprint'],
 'React meta-framework':['next','@remix-run/react','react-router','astro','@tanstack/react-start','gatsby','expo'],
 'ORM / query builder':['drizzle-orm','prisma','@prisma/client','kysely','typeorm','sequelize','mongoose'],
 'state management':['zustand','@reduxjs/toolkit','redux','jotai','mobx','valtio','recoil','pinia'],
 'schema validation':['zod','yup','joi','valibot','@sinclair/typebox','ajv','arktype'],
 'backend-as-a-service':['@supabase/supabase-js','firebase','convex','@clerk/nextjs','appwrite','pocketbase'],
 'icons':['lucide-react','react-icons','@heroicons/react','@phosphor-icons/react','@tabler/icons-react','@fortawesome/fontawesome-svg-core'],
 'CSS':['tailwindcss','styled-components','@emotion/react','sass','@mui/material','@chakra-ui/react','@mantine/core'],
 'data fetching':['@tanstack/react-query','swr','@apollo/client','axios'],
 'auth':['next-auth','better-auth','@clerk/nextjs','lucia','@auth/core','passport','@supabase/supabase-js'],
 'server framework':['express','hono','fastify','koa','@nestjs/core','elysia'],
 'toasts':['sonner','react-hot-toast','react-toastify'],
 'dates':['date-fns','dayjs','moment','luxon'],
 'monorepo':['turbo','nx','lerna'],
}
import json
def deps_of(v):
    try: p=json.loads(v['pkg'])
    except Exception: return None
    d={}
    for k in ('dependencies','devDependencies'):
        if isinstance(p.get(k),dict): d.update(p[k])
    if 'prisma' in d: d.setdefault('@prisma/client','x')
    return set(d)
def usable(meta,since='2026-10-01'):
    out=[]
    for r,v in meta.items():
        if not v or not v.get('pkg') or v['created']<since or v.get('fork'): continue
        d=deps_of(v)
        if d and len(d)>=3: out.append((r,d,v))
    return out
