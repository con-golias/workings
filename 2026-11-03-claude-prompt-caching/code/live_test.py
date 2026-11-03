"""Live A/B test of prompt caching on the Claude Messages API.

Run 1 ("off"): a small tool-using agent runs up to 10 turns with no cache_control.
Run 2 ("on"): the SAME 10 requests, byte for byte, replayed with one extra top-level field:
    "cache_control": {"type": "ephemeral"}
Only that field differs, so the difference in `usage` is caching and nothing else.

    python -I live_test.py <scenario: small|large> <out.json> [--model M] [--sections N] [--paras P]
                           [--gap-after T --gap-seconds S]
Defaults reproduce the first Haiku 5.5 runs exactly (9 sections of 9 paragraphs, up to 10 turns).
--sections N: the manual has N sections, so the agent runs up to N + 1 turns. --paras P: paragraphs per section
(9 is about 1,400 tokens). --gap-after T --gap-seconds S: in the cached pass only, wait S seconds after request T
(to show what happens when the 5-minute cache lifetime runs out between turns).
Key: ANTHROPIC_API_KEY from the environment (on Windows, also read from HKCU\\Environment). Never printed.
"""
import argparse, json, os, random, sys, time, urllib.request, urllib.error

MODEL = 'claude-haiku-5-5'  # default: cheapest current model (owner, 3 Nov: keep the test economical)
API = 'https://api.anthropic.com/v1/messages'


def api_key():
    k = os.environ.get('ANTHROPIC_API_KEY')
    if not k and sys.platform == 'win32':
        import winreg
        k = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment'), 'ANTHROPIC_API_KEY')[0]
    if not k: sys.exit('ANTHROPIC_API_KEY is not set')
    return k


def post(body, key):
    req = urllib.request.Request(API, method='POST', data=json.dumps(body).encode(),
                                 headers={'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    for attempt in range(5):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=300).read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:500]
            if e.code in (429, 500, 529) and attempt < 4: time.sleep(10 * (attempt + 1)); continue
            sys.exit(f'HTTP {e.code}: {msg}')


# ---- the agent's world: a manual of 9 sections, each a deterministic ~1,200-token text --------------------
WORDS = ('order refund shipment carrier warehouse invoice customer address parcel label tracking status return '
         'window policy exchange size colour stock restock discount tier code checkout payment receipt delay '
         'damage claim photo courier pickup weekday holiday cutoff region tax duty customs fee threshold').split()


# Readable, deterministic policy sentences (the first attempt used word salad, and the model declined to summarise it).
TEMPLATES = [
    'Orders placed before {h}:00 on a weekday leave the {wh} warehouse the same day with {c}.',
    'A customer in {r} can return an unworn item within {d} days of delivery for a full refund.',
    'Exchanges for a different size or colour are free once per order while stock lasts.',
    'If a parcel shows no tracking update for {k} working days, open a claim with {c} and tell the customer.',
    'Damaged items need one photo of the parcel and one of the item before a replacement is sent.',
    'Discount codes from the {t} tier cannot be combined with sale prices or with another code.',
    'Orders to {r} above the {f} threshold may owe import duty, which the customer pays on delivery.',
    'During holiday weeks the cutoff moves to {h2}:00 and pickups from {wh} run on {day} only.',
    'Refunds go back to the original payment method within {d2} working days of the return being checked.',
    'When an item is restocked, customers on its waiting list are emailed in the order they signed up.',
]
FILL = dict(h=['12', '13', '14', '15'], wh=['north', 'south', 'east'], c=['the national post', 'the express courier', 'the regional carrier'],
            r=['the EU', 'the UK', 'the US', 'Canada', 'Australia'], d=['14', '30', '60'], k=['3', '5', '7'],
            t=['silver', 'gold', 'platinum'], f=['150 euro', '135 pound', '800 dollar'], h2=['10', '11'],
            day=['Monday', 'Tuesday', 'Wednesday', 'Thursday'], d2=['5', '7', '10'])


def section(n, paras_per_section=9):
    rng = random.Random(1000 + n)
    paras = []
    for p in range(paras_per_section):
        sents = [rng.choice(TEMPLATES).format(**{k: rng.choice(v) for k, v in FILL.items()}) for _ in range(5)]
        paras.append(f'{n}.{p + 1} ' + ' '.join(sents))
    return f'Section {n} of the store operations manual.\n\n' + '\n\n'.join(paras)


def small_system(n=9):
    return ('You are an operations assistant for an online store. Use the read_section tool to read the store '
            f'operations manual. Read sections 1 to {n} in order, one section per turn, one tool call per turn. '
            f'After section {n}, answer with a three-sentence summary and stop.')


def tools(n=9):
    return [
    {'name': 'read_section', 'description': f'Read one numbered section (1-{n}) of the store operations manual.',
     'input_schema': {'type': 'object', 'properties': {'n': {'type': 'integer', 'description': f'Section number, 1-{n}'}}, 'required': ['n']}},
    {'name': 'lookup_order', 'description': 'Look up an order by its number and return its status.',
     'input_schema': {'type': 'object', 'properties': {'order': {'type': 'string'}}, 'required': ['order']}},
    {'name': 'search_policy', 'description': 'Search the store policies for a phrase and return matching lines.',
     'input_schema': {'type': 'object', 'properties': {'q': {'type': 'string'}}, 'required': ['q']}},
]


def large_system(n=9):
    # a long, fixed system prompt (brand voice + policies), deterministic, ~8,000 tokens
    rng = random.Random(42)
    body = []
    for i in range(90):
        sents = [rng.choice(TEMPLATES).format(**{k: rng.choice(v) for k, v in FILL.items()}) for _ in range(4)]
        body.append(f'Rule {i + 1}. ' + ' '.join(sents))
    return small_system(n) + '\n\nStore rules you must follow:\n' + '\n'.join(body)


def run_tool(block, sections=9, paras=9):
    if block['name'] == 'read_section':
        n = int(block['input'].get('n', 1))
        return section(n, paras) if 1 <= n <= sections else 'No such section.'
    return 'Not available in this test.'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scenario', choices=['small', 'large']); ap.add_argument('out')
    ap.add_argument('--model', default=MODEL); ap.add_argument('--sections', type=int, default=9)
    ap.add_argument('--paras', type=int, default=9); ap.add_argument('--gap-after', type=int, default=0)
    ap.add_argument('--gap-seconds', type=int, default=0)
    a = ap.parse_args()
    scenario, out = a.scenario, a.out
    key = api_key()
    system = small_system(a.sections) if scenario == 'small' else large_system(a.sections)
    TOOLS = tools(a.sections)
    base = {'model': a.model, 'max_tokens': 4000, 'system': system, 'tools': TOOLS,
            'tool_choice': {'type': 'auto', 'disable_parallel_tool_use': True}, 'output_config': {'effort': 'low'}}
    messages = [{'role': 'user', 'content': 'Please read the manual as instructed, then summarise it.'}]
    requests, log = [], {'scenario': scenario, 'model': a.model, 'sections': a.sections, 'paras': a.paras,
                         'gap_after': a.gap_after, 'gap_seconds': a.gap_seconds, 'started': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'off': [], 'on': []}

    # Run 1: the agent runs, no caching
    for turn in range(a.sections + 1):
        body = dict(base, messages=json.loads(json.dumps(messages)))
        requests.append(body)
        r = post(body, key)
        log['off'].append({'turn': turn + 1, 'id': r.get('id'), 'stop_reason': r.get('stop_reason'), 'usage': r.get('usage')})
        print('off', turn + 1, r.get('stop_reason'), json.dumps(r.get('usage')), flush=True)
        messages.append({'role': 'assistant', 'content': r['content']})
        uses = [b for b in r['content'] if b.get('type') == 'tool_use']
        if r.get('stop_reason') != 'tool_use' or not uses: break
        messages.append({'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': b['id'], 'content': run_tool(b, a.sections, a.paras)} for b in uses]})

    # Run 2: the identical requests, plus one top-level field
    for i, body in enumerate(requests):
        r = post(dict(body, cache_control={'type': 'ephemeral'}), key)
        log['on'].append({'turn': i + 1, 'id': r.get('id'), 'stop_reason': r.get('stop_reason'), 'usage': r.get('usage')})
        print('on ', i + 1, r.get('stop_reason'), json.dumps(r.get('usage')), flush=True)
        if a.gap_after and i + 1 == a.gap_after:
            print(f'waiting {a.gap_seconds} s', flush=True); time.sleep(a.gap_seconds)

    log['system_prompt_chars'] = len(system)
    log['tool_definitions_chars'] = len(json.dumps(TOOLS))
    json.dump(log, open(out, 'w'), indent=1)
    print('saved', out)


if __name__ == '__main__':
    main()
