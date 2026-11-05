"""All article numbers -> data/summary.json. Inputs are the files the collectors wrote (see METHOD.md)."""
import datetime as dt, json, math, os, random, statistics as st
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
J = lambda f: json.load(open(os.path.join(D, f), encoding="utf-8"))
L = lambda f: [json.loads(l) for l in open(os.path.join(D, f), encoding="utf-8")]
S = {}

# --- daily: last complete reading per day
daily = {}
for r in L("daily.jsonl"):
    daily[r["day"]] = r
calm = [daily[d] for d in sorted(daily) if "2026-10-13" <= d <= "2026-11-03"]
sh = [100 * r["claude"] / r["all"] for r in calm]
S["calm"] = {"from": "2026-10-13", "to": "2026-11-03", "days": len(calm), "median_pct": st.median(sh), "min_pct": min(sh),
             "max_pct": max(sh), "claude_per_day_median": st.median(r["claude"] for r in calm),
             "all_per_day_median": st.median(r["all"] for r in calm)}
wk = [daily[d] for d in sorted(daily) if "2026-10-26" <= d <= "2026-11-01"]
S["last_week"] = {"from": "2026-10-26", "to": "2026-11-01", "claude": sum(r["claude"] for r in wk), "all": sum(r["all"] for r in wk)}
S["last_week"]["pct"] = 100 * S["last_week"]["claude"] / S["last_week"]["all"]
S["last_week"]["one_in"] = 100 / S["last_week"]["pct"]
spike = [daily[d] for d in sorted(daily) if "2026-09-23" <= d <= "2026-10-10"]
S["spike"] = {"from": "2026-09-23", "to": "2026-10-10", "max_all": max(r["all"] for r in spike),
              "max_day": max(spike, key=lambda r: r["all"])["day"], "min_pct": min(100 * r["claude"] / r["all"] for r in spike),
              "min_pct_day": min(spike, key=lambda r: r["claude"] / r["all"])["day"]}
S["swing"] = {"max_pct": max(100 * r["claude"] / r["all"] for r in daily.values()),
              "min_pct": min(100 * r["claude"] / r["all"] for r in daily.values() if r["day"] >= "2026-08-24")}
S["swing"]["ratio"] = S["swing"]["max_pct"] / S["swing"]["min_pct"]

# --- the claim and the calibration (2 Feb 2026)
feb_all, feb_cl = 5152864, 151531          # repeat.jsonl round values (stable to <0.01%)
semi_cl, semi_pct = 134646, 4.0           # SemiAnalysis chart, data through 2026-02-02
S["feb2"] = {"all": feb_all, "claude": feb_cl, "pct": 100 * feb_cl / feb_all, "semi_claude": semi_cl, "semi_pct": semi_pct,
             "semi_implied_denominator": semi_cl / (semi_pct / 100), "our_claude_vs_semi": feb_cl / semi_cl - 1, "our_claude_vs_semi_pct": 100 * (feb_cl / semi_cl - 1)}
nov3 = daily["2026-11-03"]
S["nov3"] = {"all": nov3["all"], "claude": nov3["claude"], "pct": 100 * nov3["claude"] / nov3["all"]}
S["growth"] = {"claude_x": nov3["claude"] / feb_cl, "all_x": nov3["all"] / feb_all,
               "claude_x_needed_frozen_denominator": 0.20 * feb_all / feb_cl}

# --- projection to 31 Dec 2026 (scenarios, not forecasts)
days_fn = (dt.date(2026, 11, 3) - dt.date(2026, 2, 2)).days
days_left = (dt.date(2026, 12, 31) - dt.date(2026, 11, 3)).days
gc = (nov3["claude"] / feb_cl) ** (1 / days_fn); ga = (nov3["all"] / feb_all) ** (1 / days_fn)
cl_dec = nov3["claude"] * gc ** days_left
S["projection"] = {"days_left": days_left, "claude_daily_growth_pct": 100 * (gc - 1), "all_daily_growth_pct": 100 * (ga - 1),
                   "a_frozen_denominator_pct": 100 * cl_dec / S["calm"]["all_per_day_median"],
                   "a_growing_denominator_pct": 100 * cl_dec / (S["calm"]["all_per_day_median"] * ga ** days_left),
                   "b_last_three_weeks_flat_pct": S["calm"]["median_pct"]}
# trend inside the calm window (least squares on share vs day)
xs = list(range(len(sh))); mx, my = st.mean(xs), st.mean(sh)
slope = sum((x - mx) * (y - my) for x, y in zip(xs, sh)) / sum((x - mx) ** 2 for x in xs)
S["projection"]["calm_slope_pp_per_day"] = slope
S["projection"]["calm_trend_dec31_pct"] = my + slope * (len(sh) - 1 - mx + days_left)

# --- weekly series with spam flags
C = J("closes.json")
weeks = []
for r in L("series.jsonl"):
    w = C["weeks"].get(r["week"], {})
    spam = (w.get("spam", 0) / max(w.get("n", 1), 1)) > 0.10 or r["all"] > 150e6
    weeks.append({"week": r["week"], "all_per_day": r["all"] / 7, "claude_per_day": r["claude"] / 7,
                  "pct": 100 * r["claude"] / r["all"], "spam": spam, "spam_sample": w})
# A3: a week also counts as a flood when its total is >1.3x the mean of the two neighbouring sampled weeks
# (late May / early June 2026: 27M on 31 May vs ~7M on calm days; its 20-commit sample found no gambling spam).
for i, w in enumerate(weeks):
    nb = [weeks[j]["all_per_day"] for j in (i - 1, i + 1) if 0 <= j < len(weeks) and not weeks[j]["spam"]]
    if nb and w["all_per_day"] > 1.3 * st.mean(nb):
        w["spam"] = True; w["flood_rule"] = "neighbours"
S["weeks"] = weeks
S["spam_weeks"] = [w["week"] for w in weeks if w["spam"]]

# --- spam scale
S["spam_terms"] = {"sep24": {"caijing": 133617764, "all": daily["2026-09-24"]["all"]},
                   "nov3": {"caijing": 601826, "all": nov3["all"]}}

# --- duplicates
S["dup"] = {"all_single_repo": 100, "all_n": 100, "claude_single_repo": 98, "claude_n": 100, "claude_distinct_share": 0.988}

# --- other agents, 3 Nov
A = C["agents"]
S["agents"] = {k: v["n"] for k, v in A.items()}
S["agents"]["claude_trailer"] = nov3["claude"]
S["agents"]["claude_author_without_trailer"] = A["claude_author"]["n"] - A["claude_author_and_trailer"]["n"]
others = ["cursor", "copilot_agent", "jules", "devin", "lovable", "codex_connector", "codex_trailer", "aider", "amp", "opencode", "gemini_trailer"]
tot_other = sum(A[k]["n"] for k in others)
S["agents_share_claude_of_signed"] = 100 * nov3["claude"] / (nov3["claude"] + tot_other + S["agents"]["claude_author_without_trailer"])
S["agents_other_total"] = tot_other
S["owner"] = C["owner"]

# --- stars (cluster bootstrap by sampled hour)
stars = J("stars.json")
def load_s(f):
    R = [r for r in L(f) if stars.get(r["repo"])]
    for r in R:
        r["stars"] = stars[r["repo"]]["stargazerCount"]; r["new"] = stars[r["repo"]]["createdAt"].startswith("2026")
    return R
SA, SC = load_s("star_all_1103.jsonl"), load_s("star_claude_1103.jsonl")
frac = lambda R, k: sum(r["stars"] >= k for r in R) / len(R)
S["stars"] = {"n_all": len(SA), "n_claude": len(SC), "repos_all": len({r["repo"] for r in SA}), "repos_claude": len({r["repo"] for r in SC})}
for k in (1, 2, 10, 100, 1000):
    S["stars"][f"all_ge{k}"] = 100 * frac(SA, k); S["stars"][f"claude_ge{k}"] = 100 * frac(SC, k)
S["stars"]["all_zero"] = 100 * sum(r["stars"] == 0 for r in SA) / len(SA)
S["stars"]["claude_zero"] = 100 * sum(r["stars"] == 0 for r in SC) / len(SC)
S["stars"]["all_new2026"] = 100 * sum(r["new"] for r in SA) / len(SA)
S["stars"]["claude_new2026"] = 100 * sum(r["new"] for r in SC) / len(SC)
random.seed(1)
hA = {}; hC = {}
for r in SA: hA.setdefault(r["hour"], []).append(r)
for r in SC: hC.setdefault(r["hour"], []).append(r)
def share_ge(k, p=S["nov3"]["pct"]):
    a = frac(SA, k); c = frac(SC, k)
    return p * c / a if a else float("nan")
boots = []
for _ in range(2000):
    ra = [r for h in random.choices(list(hA), k=len(hA)) for r in hA[h]]
    rc = [r for h in random.choices(list(hC), k=len(hC)) for r in hC[h]]
    a = frac(ra, 100); c = frac(rc, 100)
    if a: boots.append(S["nov3"]["pct"] * c / a)
boots.sort()
S["stars"]["share_in_ge100_pct"] = share_ge(100)
S["stars"]["share_in_ge100_ci"] = [boots[int(.025 * len(boots))], boots[int(.975 * len(boots))]]
S["stars"]["share_in_ge10_pct"] = share_ge(10)

# --- scheduled-looking commits (crude classifier, same rule on both samples): bot/github-actions author, or a message
# that starts like a routine update (date, "update", "refresh", "sync", "daily", "status", "data", "bump", "[skip ci]")
import re
AUTO = re.compile(r"^(update|auto|automated|refresh|sync|daily|data|status|chore: update|bump|\d{4}-\d{2}-\d{2}|sport and news|\[skip ci\])", re.I)
BOT = re.compile(r"\[bot\]|github-actions", re.I)
sched = lambda R: sum(1 for r in R if AUTO.match(r["message"].strip()) or BOT.search(r["author_name"])) / len(R)
S["scheduled"] = {"all_pct": 100 * sched(SA), "claude_pct": 100 * sched(SC)}
S["scheduled"]["share_among_unscheduled_pct"] = S["nov3"]["pct"] * (1 - sched(SC)) / (1 - sched(SA))
S["stars"]["distinct_repos_ge100_all"] = len({r["repo"] for r in SA if r["stars"] >= 100})
S["stars"]["distinct_repos_ge100_claude"] = len({r["repo"] for r in SC if r["stars"] >= 100})
S["codex_trailer_verified"] = "20 of 20 full messages carry a literal Co-authored-by: Codex line (3 Nov)"
# --- facts read by hand at the sources listed in the article
S["facts"] = {
    "semi_post_views_k": 621.2, "semi_chart_growth_x": 42896,
    "models_n": 100, "models": {"opus_5_5": 70, "sonnet_5_5": 24, "opus_5_5_1m": 4, "sonnet_4_6": 1, "haiku_5_5": 1},
    "spam_sample": {"n": 100, "spam": 79, "repos": 11, "day": "24 Sep"},
    "tracker_mar15_claude_then": 326731, "mar15_claude_now": 337736,
    "tracker_mar16_week_then_m": 2.6, "mar16_week_claude_now": 2553070, "mar16_week_all_now": 46018496,
    "octoverse_2025_commits_m": 986, "octoverse_2026_commits_b": 34.3, "octoverse_2026_x": 6,
    "octoverse_2026_new_repo_share": 55, "octoverse_2026_agent_pr_share": 40, "octoverse_2026_agent_pr_march": 17,
    "repeat_rounds": 4, "repeat_days": 5, "spam_reachable": 3,
    "trailer_in_all_sample": 26, "all_sample_n": 200,
    "sampled_weeks": len(weeks), "flood_weeks": sum(w["spam"] for w in weeks),
}
S["daily"] = [{"day": d, "all": daily[d]["all"], "claude": daily[d]["claude"]} for d in sorted(daily) if d >= "2026-08-24"]
json.dump(S, open(os.path.join(D, "summary.json"), "w"), indent=1)
print(json.dumps({k: S[k] for k in ["calm", "last_week", "spike", "swing", "feb2", "nov3", "growth", "projection", "spam_weeks", "agents_share_claude_of_signed", "owner"]}, indent=1))
print(json.dumps(S["stars"], indent=1)); print(S["agents"])
