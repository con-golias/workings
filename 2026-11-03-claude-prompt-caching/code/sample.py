"""Draw the pre-registered hand-check sample (seed 20261103) from scan.csv.  python -I sample.py scan.csv out.csv"""
import csv, random, sys
rows = sorted(csv.DictReader(open(sys.argv[1], encoding='utf-8')), key=lambda x: x['repo'])
rng = random.Random(20261103)
v2 = [x for x in rows if x['bucket'] == 'agent']
groups = [
    ('v2_marker', [x for x in v2 if x['caching_marker'] == '1'], 30),
    ('v2_no_marker', [x for x in v2 if x['caching_marker'] == '0'], 30),
    ('v1_minus_v2', [x for x in rows if x['agent_v1'] == '1' and x['bucket'] != 'agent'], 15),
    ('loose_minus_v2', [x for x in rows if x['agent_loose'] == '1' and x['bucket'] != 'agent'], 15),
]
with open(sys.argv[2], 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['group', 'repo', 'sha', 'direct', 'loop_same_file', 'cache_markers'])
    for g, pool, n in groups:
        for x in rng.sample(pool, n): w.writerow([g, x['repo'], x['sha'], x['direct'], x['loop_same_file'], x['cache_markers']])
        print(g, len(pool), n)
