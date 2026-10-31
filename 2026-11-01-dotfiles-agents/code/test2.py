# The test written before the full run, in its first version and the version amended after a dry run. numpy for the bootstrap.
# Share in year Y = repos with >=1 commit in Y whose year-end snapshot has the signal.
# Emergence = first year >= 3%; a tool already >= 3% in 2015 has no clear start (excluded, reported).
# Original (as first coded): takeoff = years to 20%, never = inf; early median_low vs late median_high.
# Amended: window W = 3 years, only tools that emerged <= 2023; not inside the window = 4; plain median both sides.
# Keep only if early - late >= 1 year AND that holds in >= 90% of 1,000 bootstrap resamples over repos.
import json, sys, statistics
import numpy as np
TOOLS = "fzf ripgrep bat fd delta exa starship zoxide direnv lazygit atuin eza mise uv alacritty kitty wezterm ghostty zellij hyprland neovim catppuccin tokyonight rosepine kanagawa everforest nord dracula onedark jetbrainsmono ai_claude ai_agentsmd ai_opencode ai_codex".split()
YEARS = list(range(2015, 2027)); INF = float("inf"); W = 3
rows = [r for r in json.load(open(sys.argv[1])) if r["commits"] > 0 and r["year"] in YEARS]
repos = sorted({r["repo"] for r in rows}); ri = {n: i for i, n in enumerate(repos)}
R = np.array([ri[r["repo"]] for r in rows]); Y = np.array([r["year"] - 2015 for r in rows])
M = np.array([[r[t] for t in TOOLS] for r in rows], dtype=float)
def shares(w):  # w = weight per repo (1 each, or bootstrap counts)
    wr = w[R]; n = np.bincount(Y, weights=wr, minlength=len(YEARS))
    h = np.stack([np.bincount(Y, weights=wr * M[:, j], minlength=len(YEARS)) for j in range(len(TOOLS))], 1)
    return h / np.maximum(n, 1)[:, None], n
def classify(sh):
    out = {}
    for j, t in enumerate(TOOLS):
        s = sh[:, j]; e = np.nonzero(s >= 0.03)[0]
        if not len(e): out[t] = ("never3", None, None, None); continue
        em = int(e[0])
        if em == 0: out[t] = ("no_start", 2015, None, None); continue
        h = np.nonzero(s[em:] >= 0.20)[0]
        orig = int(h[0]) if len(h) else INF
        amend = (min(orig, W + 1) if orig <= W else W + 1) if em + 2015 <= 2026 - W else None
        out[t] = ("ok" if len(h) else "censored", em + 2015, orig, amend)
    return out
def diffs(c):
    eo = sorted(v[2] for v in c.values() if v[1] and v[0] in ("ok", "censored") and v[1] <= 2019)
    lo = sorted(v[2] for v in c.values() if v[1] and v[0] in ("ok", "censored") and v[1] >= 2021)
    ea = sorted(v[3] for v in c.values() if v[3] is not None and v[1] <= 2019)
    la = sorted(v[3] for v in c.values() if v[3] is not None and v[1] >= 2021)
    d_o = None
    if eo and lo:
        a, b = statistics.median_low(eo), statistics.median_high(lo)
        d_o = 0 if a == b == INF else a - b
    d_a = statistics.median(ea) - statistics.median(la) if ea and la else None
    return d_o, d_a, (eo, lo, ea, la)
sh, n = shares(np.ones(len(repos)))
c = classify(sh); d_o, d_a, (eo, lo, ea, la) = diffs(c)
print("repos", len(repos), "active per year:", dict(zip(YEARS, n.astype(int).tolist())))
for j, t in enumerate(TOOLS):
    st, em, o, a = c[t]
    print(f"{t:14s} {st:9s} emerge={em} orig={o} amended={a}  " + " ".join(f"{x*100:4.0f}" for x in sh[:, j]))
print("ORIGINAL  early", eo, "late", lo, "diff", d_o)
print("AMENDED   early", ea, "median", statistics.median(ea) if ea else None, "| late", la, "median", statistics.median(la) if la else None, "diff", d_a)
rng = np.random.default_rng(2026); B = 1000; po = pa = 0; bd = []
for b in range(B):
    w = np.bincount(rng.integers(0, len(repos), len(repos)), minlength=len(repos)).astype(float)
    xo, xa, _ = diffs(classify(shares(w)[0])); bd.append(xa)
    po += xo is not None and xo >= 1; pa += xa is not None and xa >= 1
v = lambda d, p: "keep" if d is not None and d >= 1 and p / B >= 0.9 else "drop"
print(f"ORIGINAL bootstrap {po}/{B}  verdict {v(d_o, po)}")
print(f"AMENDED  bootstrap {pa}/{B}  verdict {v(d_a, pa)}")
json.dump({"repos": len(repos), "active": dict(zip(YEARS, n.tolist())), "shares": {t: dict(zip(YEARS, sh[:, j].round(4).tolist())) for j, t in enumerate(TOOLS)},
           "classes": c, "original": {"diff": d_o, "boot": po / B, "verdict": v(d_o, po)},
           "amended": {"diff": d_a, "boot": pa / B, "verdict": v(d_a, pa), "boot_diffs": bd}}, open(sys.argv[2], "w"), default=str)
