"""scan.csv + handcheck → summary.json.   python -I analyze.py   (run from the article folder)"""
import csv, json, os, random, collections
D = 'data/'
scan = list(csv.DictReader(open(D + 'scan.csv', encoding='utf-8')))
uni = [l.strip() for l in open(D + 'universe.txt') if l.strip()]
miss = [l.strip() for l in open(D + 'missing.txt') if l.strip()]
samp = list(csv.DictReader(open(D + 'handcheck_sample.csv', encoding='utf-8')))
verd = {r['repo']: r for r in csv.DictReader(open(D + 'handcheck_verdicts.csv', encoding='utf-8'))}
assert len(verd) == len(samp) == 90 and all(s['repo'] in verd for s in samp)

def share(rows):
    n = len(rows); k = sum(r['caching_marker'] == '0' for r in rows)
    return dict(n=n, no_marker=k, pct=round(100 * k / n, 1))

v2 = [r for r in scan if r['bucket'] == 'agent']
pools = {
    'v2_marker': [r for r in v2 if r['caching_marker'] == '1'],
    'v2_no_marker': [r for r in v2 if r['caching_marker'] == '0'],
    'v1_minus_v2': [r for r in scan if r['agent_v1'] == '1' and r['bucket'] != 'agent'],
    'loose_minus_v2': [r for r in scan if r['agent_loose'] == '1' and r['bucket'] != 'agent'],
}
# v1-minus-v2 and loose-minus-v2 overlap. To keep the strata disjoint, the loose stratum is restricted to repos
# outside v1 (its pool and its sampled rows alike); its sampled rows inside v1 are not used.
v1set = {r['repo'] for r in pools['v1_minus_v2']}
pools['loose_minus_v2'] = [r for r in pools['loose_minus_v2'] if r['repo'] not in v1set]
strata = {g: [verd[s['repo']] for s in samp if s['group'] == g and not (g == 'loose_minus_v2' and s['repo'] in v1set)] for g in pools}

def estimate(strata, count_unsure=False):
    """Estimated number of real agents in the scanned repos, and how many of them have caching on."""
    agents = cached = 0.0
    for g, rows in strata.items():
        N, n = len(pools[g]), len(rows)
        isag = [r for r in rows if r['is_agent'] == 'yes' or (count_unsure and r['is_agent'] == 'unsure')]
        agents += N * len(isag) / n
        cached += N * sum(r['caching_on'] in ('yes', 'auto') for r in isag) / n
    return agents, cached

def boot(count_unsure=False, B=20000, seed=20261103):
    rng = random.Random(seed); vals = []
    for _ in range(B):
        s = {g: [rng.choice(rows) for _ in rows] for g, rows in strata.items()}
        a, c = estimate(s, count_unsure)
        if a: vals.append(100 * (a - c) / a)
    vals.sort(); return [round(vals[int(0.025 * len(vals))], 1), round(vals[int(0.975 * len(vals))], 1)]

out = {}
out['universe'] = len(uni); out['cloned'] = len(scan); out['gone'] = len(miss)
out['buckets'] = dict(collections.Counter(r['bucket'] for r in scan))
out['agent_sdk_or_claude_code_any'] = sum(1 for r in scan if r['agent_sdk'])
out['agent_sdk_only'] = out['buckets'].get('agent_sdk_only', 0)
out['agent_sdk_also_direct'] = out['agent_sdk_or_claude_code_any'] - out['agent_sdk_only']
out['openai_compat_claude_in_no_direct'] = sum(1 for r in scan if r['bucket'] == 'no_direct_call' and r['openai_compat_claude'])
out['regex'] = dict(v2=share(v2), v1=share([r for r in scan if r['agent_v1'] == '1']), loose=share([r for r in scan if r['agent_loose'] == '1']),
                    v2_without_agent_sdk_repos=share([r for r in v2 if not r['agent_sdk']]))
hc = {}
for g, rows in strata.items():
    hc[g] = dict(pool=len(pools[g]), n=len(rows), kinds=dict(collections.Counter(r['kind'] for r in rows)),
                 is_agent=dict(collections.Counter(r['is_agent'] for r in rows)),
                 caching_among_agents=dict(collections.Counter(r['caching_on'] for r in rows if r['is_agent'] == 'yes')))
out['handcheck'] = hc
pos = strata['v2_marker']; neg = strata['v2_no_marker']
out['precision'] = dict(
    marker_side=dict(real_agent_with_caching=sum(r['is_agent'] == 'yes' and r['caching_on'] == 'yes' for r in pos), of=len(pos)),
    no_marker_side=dict(real_agent_without_caching=sum(r['is_agent'] == 'yes' and r['caching_on'] == 'no' for r in neg), of=len(neg)))
for key, cu in (('main', False), ('unsure_counted_as_agents', True)):
    a, c = estimate(strata, cu)
    out['corrected_' + key] = dict(est_agents=round(a, 1), est_with_caching=round(c, 1), est_without=round(a - c, 1),
                                   pct_without=round(100 * (a - c) / a, 1), ci95_bootstrap=boot(cu))
# robustness: every repo that calls the Messages API directly, whatever the agent definition
direct = [r for r in scan if r['bucket'] in ('agent', 'direct_no_loop')]
out['all_direct_callers'] = share(direct)
out['handcheck_real_agents'] = sum(r['is_agent'] == 'yes' for r in verd.values())
out['handcheck_learning_repos'] = sum(r['is_agent'] == 'yes' and r['learning'] == 'yes' for r in verd.values())  # courses, tutorials, starters, demos

# ---- live test (data/live/*.json): measured usage, priced at list prices read 3 Nov 2026, per million tokens ----
PRICES = {  # input, 5-minute cache write, cache read, output
    'haiku_5_5': (0.10, 0.125, 0.01, 0.50),   # <=100K-token requests
    'sonnet_5_5': (2.0, 2.50, 0.10, 10.0),
    'opus_5_5': (4.0, 5.0, 0.20, 20.0),
}
live = {}
LIVE_FILES = {'small': 'small', 'large': 'large', 'sonnet_small': 'sonnet-small', 'sonnet_large': 'sonnet-large',
              'sonnet_long': 'sonnet-long', 'sonnet_small_repeat': 'sonnet-small-repeat', 'haiku_ttl_gap': 'haiku-ttl-gap'}
MODEL_KEY = {'claude-haiku-5-5': 'haiku_5_5', 'claude-sonnet-5-5': 'sonnet_5_5', 'claude-opus-5-5': 'opus_5_5'}
spend = 0.0
for sc, fname in LIVE_FILES.items():
    if not os.path.exists(D + f'live/{fname}.json'): continue
    d = json.load(open(D + f'live/{fname}.json', encoding='utf-8'))
    L = {'turns': len(d['off']), 'system_prompt_chars': d['system_prompt_chars'], 'model': d['model'],
         'stop_reasons': sorted({t['stop_reason'] for t in d['off'] + d['on']})}
    pi, pw, pr, po = PRICES[MODEL_KEY[d['model']]]
    for t in d['off'] + d['on']:  # what the run actually cost, output included
        u = t['usage']; spend += (u['input_tokens'] * pi + u['cache_creation_input_tokens'] * pw + u['cache_read_input_tokens'] * pr + u['output_tokens'] * po) / 1e6
    for run in ('off', 'on'):
        us = [t['usage'] for t in d[run]]
        L[run] = dict(input_total=sum(u['input_tokens'] + u['cache_creation_input_tokens'] + u['cache_read_input_tokens'] for u in us),
                      full_price=sum(u['input_tokens'] for u in us), written=sum(u['cache_creation_input_tokens'] for u in us),
                      read=sum(u['cache_read_input_tokens'] for u in us), output=sum(u['output_tokens'] for u in us),
                      per_turn=[[u['input_tokens'], u['cache_creation_input_tokens'], u['cache_read_input_tokens']] for u in us])
        L[run]['turn1'] = L[run]['per_turn'][0]; L[run]['last'] = L[run]['per_turn'][-1]
    assert L['off']['input_total'] == L['on']['input_total'], 'replay must send identical tokens'
    L['last_turn_total'] = sum(L['off']['last'])
    cost = {}
    for m, (pi, pw, pr, po) in PRICES.items():
        # input side only: both runs are priced with the same token counts; output is identical in kind and left out
        off = L['off']['full_price'] * pi / 1e6
        on = (L['on']['full_price'] * pi + L['on']['written'] * pw + L['on']['read'] * pr) / 1e6
        cost[m] = dict(off=round(off, 6), on=round(on, 6), on_pct=round(100 * on / off, 1), saved_pct=round(100 - 100 * on / off, 1),
                       off_per_1000=round(off * 1000, 2), on_per_1000=round(on * 1000, 2), saved_per_1000=round((off - on) * 1000, 2))
    L['cost_input_side'] = cost
    live[sc] = L
out['live'] = live
out['live_spend_reported_runs'] = round(spend, 2)  # the stopped first Sonnet attempt (about $0.20) is not in these files
# the stopped first attempt on Sonnet 5.5 (its usage lines are in the .log)
import re as _re
stopped = 0.0
for line in open(D + 'live/sonnet-5-5-first-attempt-stopped.log', encoding='utf-8'):
    m = _re.search(r'(\{.*\})', line)
    if m:
        u = json.loads(m.group(1)); pi, pw, pr, po = PRICES['sonnet_5_5']
        stopped += (u['input_tokens'] * pi + u['cache_creation_input_tokens'] * pw + u['cache_read_input_tokens'] * pr + u['output_tokens'] * po) / 1e6
out['live_spend_stopped_attempt'] = round(stopped, 2)
out['live_spend_total'] = round(spend + stopped, 2)
out['est_agents_round'] = round(out['corrected_main']['est_agents'])
out['pct_without_round'] = round(out['corrected_main']['pct_without'])

# ---- numbers quoted from sources (read 3 Nov 2026), kept here so every number in the article traces to one file ----
out['sources'] = {
    'paper_2610_34817': dict(prs=120, apps=10, silent=108, silent_pct=90, gating=37, gating_pct=31, volatile=13, volatile_pct=11,
                             repos=571, warnings=37, tp=32, fp=5, projects=33, precision=0.86, confirmed=21, fixed=18),
    'paper_2601_06007': dict(saving_lo=41, saving_hi=80, sessions=500, system_tokens=10000),
    'anthropic': dict(min_tokens_new=512, min_tokens_mid=1024, min_tokens_old=4096, read_x=0.1, read_x_55=0.05, read_x_fable=0.025,
                      write_5m_x=1.25, write_1h_x=2, ttl_min=5, tool_prompt_tokens_55=286, launch_up_to_pct=90,
                      haiku_55_in=0.10, sonnet_55_in=2, sonnet_55_read=0.10, opus_55_in=4, opus_55_read=0.20),
    'openai': dict(min_tokens=1024, up_to_pct=95),
    'google': dict(min_tokens_new=4096, min_tokens_25=2048),
}
json.dump(out, open(D + 'summary.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
