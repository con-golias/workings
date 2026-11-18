"""Derive the article's numbers from data/paper_numbers.json (typed from the paper, each with its reference).
Only differences and shares are computed here; nothing is re-estimated (the paper released no data).
  python code/analysis.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data")
P = json.load(open(os.path.join(DATA, "paper_numbers.json"), encoding="utf-8"))
s1, s2, r = P["study1"], P["study2"], P["related"]
v = lambda x: x[0]
vals = lambda d: [x for k, x in d.items() if not k.startswith("_")]
S = dict(
    answers=v(s1["answers"]), prompts=v(s1["prompts"]), brands=v(s1["brands"]), rankings=v(s2["rankings"]),
    rankings_all=v(s2["rankings"]) + v(s2["rankings_real_product"]), questions=v(s2["questions"]),
    gemini_searched=v(s1["searched_pct"]["Gemini"]),
    top_q_low=v(s1["top_quintile_vs_average"])[0], top_q_high=v(s1["top_quintile_vs_average"])[1],
    top_share_low=v(s1["mention_share_top_quintile_pct"])[0], top_share_high=v(s1["mention_share_top_quintile_pct"])[1],
    slope_off=v(s1["slope_search_off"]), slope_on=v(s1["slope_search_on"]),
    slope_none=v(s1["persona_slopes"]["none"]), slope_a=v(s1["persona_slopes"]["A_baseline"]),
    slope_b=v(s1["persona_slopes"]["B_price"]), slope_c=v(s1["persona_slopes"]["C_profile"]),
    persona_cut_pct=round(100 * (v(s1["persona_slopes"]["none"]) - v(s1["persona_slopes"]["A_baseline"])) / v(s1["persona_slopes"]["none"])),
    price_q_low=v(s1["price_word_in_queries_with_persona_pct"])[0], price_q_high=v(s1["price_word_in_queries_with_persona_pct"])[1],
    price_q0_low=v(s1["price_word_without_persona_pct"])[0], price_q0_high=v(s1["price_word_without_persona_pct"])[1],
    travel_first_low=v(s1["first_search_travel_pct"])[0], travel_first_high=v(s1["first_search_travel_pct"])[1],
    ins_first_low=v(s1["first_search_insurance_pct"])[0], ins_first_high=v(s1["first_search_insurance_pct"])[1],
    third_party=v(s1["third_party_only_pct"]["all"]), third_gpt=v(s1["third_party_only_pct"]["GPT"]),
    third_gemini=v(s1["third_party_only_pct"]["Gemini"]), third_pplx=v(s1["third_party_only_pct"]["Perplexity"]),
    rank_true=v(s2["rank_true_brand"]), rank_invented=v(s2["rank_invented_brand"]),
    brand_gain=v(s2["h4a_true_vs_invented"]), brand_gain_lo=s2["h4a_true_vs_invented"][1][0], brand_gain_hi=s2["h4a_true_vs_invented"][1][1],
    product_name=v(s2["h4b_real_vs_invented_product"]), brand_alone=v(s2["brand_name_alone"]),
    product_name_lo=s2["h4b_real_vs_invented_product"][1][0], product_name_hi=s2["h4b_real_vs_invented_product"][1][1],
    brand_alone_lo=s2["brand_name_alone"][1][0], brand_alone_hi=s2["brand_name_alone"][1][1],
    lk_lo=s2["h4e_less_known_vs_invented"][1][0], lk_hi=s2["h4e_less_known_vs_invented"][1][1],
    less_known_vs_invented=v(s2["h4e_less_known_vs_invented"]), better_vs_less=v(s2["h4c_better_vs_less_known"]),
    rewrite=v(s2["h5a_rewrite"]), rewrite_lo=s2["h5a_rewrite"][1][0], rewrite_hi=s2["h5a_rewrite"][1][1],
    rewrite_cap=v(s2["rewrite_rules_out_above"]),
    brand_minus_rewrite=v(s2["h5b_brand_minus_rewrite"]), bmr_lo=s2["h5b_brand_minus_rewrite"][1][0], bmr_hi=s2["h5b_brand_minus_rewrite"][1][1],
    leak=v(s2["brand_recognition_leak_pct"]), gpt_on_gpt=v(s2["rewrite_gpt_on_gpt_extra"]),
    loo_low=v(s2["leave_one_out_range"])[0], loo_high=v(s2["leave_one_out_range"])[1],
    by_model=s2["h4a_by_model"], by_sector=s2["h4a_by_sector"], rw_model=s2["h5a_by_model"], rw_sector=s2["h5a_by_sector"],
    model_min=min(vals(s2["h4a_by_model"])), model_max=max(vals(s2["h4a_by_model"])),
    rewrite_max_cell=max(max(vals(s2["h5a_by_model"])), max(vals(s2["h5a_by_sector"]))),
    geo_40=v(r["geo_2023_visibility_up_to_pct"]), safegeo=v(r["safegeo_pp"]), safegeo_def=v(r["safegeo_defense_pp"]),
    chu_star=v(r["chu_hou_rating_star"]), chu_pay_hi=v(r["chu_hou_payoff"])[0], chu_pay_lo=v(r["chu_hou_payoff"])[1],
)
# added 9 Nov 2026 for the new figures 4-6: search rates and where the brand was found, per engine (Table 1, 4.1, 3.2)
S.update(searched_gpt=v(s1["searched_pct"]["GPT"]), searched_pplx=v(s1["searched_pct"]["Perplexity"]),
         found_gpt=v(s1["name_in_returned_source_pct"]["GPT"]), found_gemini=v(s1["name_in_returned_source_pct"]["Gemini"]),
         found_pplx=v(s1["name_in_returned_source_pct"]["Perplexity"]), gemini_unverifiable=v(s1["gemini_unverifiable_pct"]))
json.dump(S, open(os.path.join(DATA, "summary.json"), "w"), indent=1)
print(json.dumps({k: S[k] for k in ("brand_gain", "rewrite", "brand_minus_rewrite", "persona_cut_pct", "model_min", "model_max", "rewrite_max_cell")}))
