"""Classify every cloned repo by how it calls Claude and whether its source turns prompt caching on.

Reads files straight from git's object store at the recorded HEAD (no checkout), so paths that
Windows cannot write are still scanned. Usage:
    python -I scan.py <repos_dir> <shas.csv> <out.csv>
Rules: see NOTES.md, "Method (pre-registered 3 Nov 2026)".
"""
import csv, os, re, subprocess, sys

SRC = ('.py', '.ts', '.tsx', '.js', '.mjs', '.cjs', '.jsx', '.go', '.java', '.kt', '.rb', '.cs', '.rs', '.php', '.swift', '.ipynb')
CFG = ('.yaml', '.yml', '.json', '.toml')           # scanned for cache markers only (e.g. LiteLLM injection points)
SKIP_DIR = re.compile(r'(^|/)(node_modules|dist|build|out|\.next|\.venv|venv|env|site-packages|vendor|third_party|\.git|__pycache__|coverage)(/|$)')
SKIP_FILE = re.compile(r'(\.min\.js|\.bundle\.js|package-lock\.json|pnpm-lock\.yaml|yarn\.lock)$')
MAX_BYTES = 1_000_000

# A file "calls the Messages API directly" (any of these):
DIRECT = re.compile(
    r'\.messages\.(?:create|stream|parse)\s*\('                    # official SDKs (py/ts/rb/…): client.messages.create(
    r'|\.Messages\.New\s*\(|\.Messages\.NewStreaming\s*\('        # Go SDK
    r'|messages\(\)\.create\s*\('                                   # Java/Kotlin SDK
    r'|tool_runner\s*\(|toolRunner\s*\('                            # SDK tool runner (beta)
    r'|api\.anthropic\.com/v1/messages|["\']/v1/messages["\']'      # raw HTTP
    r'|\bChatAnthropic\s*\('                                        # LangChain
    r'|@ai-sdk/anthropic|\bcreateAnthropic\s*\('                    # Vercel AI SDK
    r'|\bAnthropicVertex\s*\(|\bAnthropicBedrock\s*\('              # Vertex / Bedrock clients from the SDK
)
LITELLM = re.compile(r'\blitellm\.a?completion\s*\(|from litellm import')
CLAUDE_STR = re.compile(r'["\'](?:anthropic/)?claude-[a-z0-9.\-]+["\']')
# Agent SDK / Claude Code: the SDK builds the request (Claude Code docs: "automatically optimizes costs through prompt caching")
AGSDK = re.compile(r'claude_agent_sdk|@anthropic-ai/claude-agent-sdk|claude_code_sdk|@anthropic-ai/claude-code\b|["\']claude["\']\s*,\s*["\']-p["\']')
# Claude through an OpenAI-compatible client (OpenRouter, Anthropic's OpenAI-compat endpoint): reported, not classified
COMPAT = re.compile(r'openrouter\.ai/api|api\.anthropic\.com/v1/?["\']|["\']anthropic/claude-')
# A tool loop in the same file as the call
LOOP_V1 = re.compile(r'tool_use|tool_result|stop_reason|stopReason|toolUse\b|tool-call|tool-result|bind_tools|create_react_agent|\bcreate_agent\s*\(|AgentExecutor|tool_runner|toolRunner|stopWhen|maxSteps')  # pre-registered, kept as a column
LOOP = re.compile(r'tool_use|tool_result|toolUse\b|tool-call|tool-result|bind_tools|create_react_agent|\bcreate_agent\s*\(|AgentExecutor|tool_runner|toolRunner|stopWhen|maxSteps')  # Amendment 1: no stop_reason
TOOLS_ANY = re.compile(r'\btools\s*[=:]|["\']tools["\']\s*:|tool_use|bind_tools')
TOOLS_FILE = re.compile(r'\btools\s*[=:]|["\']tools["\']\s*:|\bTools\s*:|\.tools\s*\(|addTool\s*\(|bind_tools|create_react_agent|\bcreate_agent\s*\(|AgentExecutor|tool_runner|toolRunner')
TESTPATH = re.compile(r'(^|/)(tests?|__tests__|spec|specs|mocks?|__mocks__|fixtures?)(/|$)|(^|/)(test_[^/]*|[^/]*_test\.\w+|[^/]*\.(test|spec)\.\w+)$', re.I)
# Caching turned on
CACHE = re.compile(r'cache_control|cacheControl|cache_control_injection_points|AnthropicPromptCachingMiddleware|cachePoint|cache_point')

def blobs(repo, sha):
    out = subprocess.run(['git', '-C', repo, 'ls-tree', '-r', '-z', '--long', sha], capture_output=True).stdout
    for ent in out.split(b'\0'):
        if not ent: continue
        meta, path = ent.split(b'\t', 1)
        mode, typ, oid, size = meta.split()
        if typ != b'blob' or size == b'-' or int(size) > MAX_BYTES: continue
        p = path.decode('utf-8', 'replace')
        low = p.lower()
        if SKIP_DIR.search(p) or SKIP_FILE.search(low): continue
        if low.endswith(SRC) or low.endswith(CFG):
            yield p, oid.decode()

def read_all(repo, items):
    if not items: return {}
    proc = subprocess.run(['git', '-C', repo, 'cat-file', '--batch'], input=('\n'.join(o for _, o in items) + '\n').encode(), capture_output=True)
    data, res, i = proc.stdout, {}, 0
    for p, o in items:
        nl = data.index(b'\n', i); hdr = data[i:nl].split(); n = int(hdr[2])
        res[p] = data[nl + 1: nl + 1 + n].decode('utf-8', 'replace'); i = nl + 1 + n + 1
    return res

def first(rx, text):
    m = rx.search(text)
    return (text.count('\n', 0, m.start()) + 1) if m else 0

def scan(repo, sha):
    files = read_all(repo, list(blobs(repo, sha)))
    r = dict(n_files=len(files), direct=[], loop_same=[], cache=[], agsdk=[], compat=[], tools_any=False, v1=False, v2=False)
    for p, t in files.items():
        src = p.lower().endswith(SRC)
        if CACHE.search(t): r['cache'].append(f'{p}#L{first(CACHE, t)}')
        if not src: continue
        d = first(DIRECT, t) or (first(LITELLM, t) if CLAUDE_STR.search(t) else 0)
        if d:
            r['direct'].append(f'{p}#L{d}')
            if LOOP_V1.search(t): r['v1'] = True
            if not TESTPATH.search(p) and LOOP.search(t) and TOOLS_FILE.search(t):
                r['v2'] = True; r['loop_same'].append(f'{p}#L{first(LOOP, t)}')
        if AGSDK.search(t): r['agsdk'].append(f'{p}#L{first(AGSDK, t)}')
        if COMPAT.search(t): r['compat'].append(f'{p}#L{first(COMPAT, t)}')
        if TOOLS_ANY.search(t): r['tools_any'] = True
    if not r['direct']: bucket = 'agent_sdk_only' if r['agsdk'] else 'no_direct_call'
    elif r['v2']: bucket = 'agent'
    else: bucket = 'direct_no_loop'
    r['bucket'] = bucket
    r['agent_loose'] = bool(r['direct']) and r['tools_any']
    r['agent_v1'] = r['v1']
    return r

def main():
    repos_dir, shas_csv, out_csv = sys.argv[1:4]
    rows = list(csv.DictReader(open(shas_csv, encoding='utf-8')))
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['repo', 'sha', 'bucket', 'agent_v1', 'agent_loose', 'caching_marker', 'n_files', 'direct', 'loop_same_file', 'cache_markers', 'agent_sdk', 'openai_compat_claude'])
        for k, row in enumerate(rows):
            d = os.path.join(repos_dir, row['repo'].replace('/', '__', 1))
            r = scan(d, row['sha'])
            j = lambda xs: ' '.join(xs[:5])
            w.writerow([row['repo'], row['sha'], r['bucket'], int(r['agent_v1']), int(r['agent_loose']), int(bool(r['cache'])), r['n_files'], j(r['direct']), j(r['loop_same']), j(r['cache']), j(r['agsdk']), j(r['compat'])])
            if k % 100 == 0: print(k, file=sys.stderr)

if __name__ == '__main__':
    main()
