"""data/inputs.json -> data/summary.json. Every derived number in the article is computed here from the inputs
(each input carries its source in inputs.json). Run: python code/compute.py"""
import json, os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I = {k: v["v"] for k, v in json.load(open(os.path.join(root, "data", "inputs.json"), encoding="utf-8")).items() if not k.startswith("_")}
S = dict(I)

# Unitree: average price per humanoid sold, and what "industry" leaves once showroom tours are taken out
rev, units = I["unitree_humanoid_rev_yuan_m"], I["unitree_units_sold"]
S["unitree_asp_yuan_k"] = {y: round(rev[y] * 1000 / units[y], 1) for y in rev}
sp = I["unitree_split_jan_sep_2025_yuan_m"]
ind = sp["industry"]
S["unitree_work_yuan_m_low"] = round(ind * (1 - I["unitree_industry_tours_share_high_pct"] / 100), 1)
S["unitree_work_yuan_m_high"] = round(ind * (1 - I["unitree_industry_tours_share_low_pct"] / 100), 1)
S["unitree_work_pct_low"] = round(100 * S["unitree_work_yuan_m_low"] / sp["total"], 1)
S["unitree_work_pct_high"] = round(100 * S["unitree_work_yuan_m_high"] / sp["total"], 1)
S["unitree_tours_pct_low"] = round(100 * ind * I["unitree_industry_tours_share_low_pct"] / 100 / sp["total"], 1)
S["unitree_tours_pct_high"] = round(100 * ind * I["unitree_industry_tours_share_high_pct"] / 100 / sp["total"], 1)
S["unitree_growth_units_2025_vs_2024"] = round(units["2025"] / units["2024"], 1)
S["unitree_drop_from_debut_pct"] = round(100 * (1 - I["unitree_sep9_close_yuan"] / I["unitree_debut_close_yuan"]), 0)
S["unitree_sep9_vs_ipo_x"] = round(I["unitree_sep9_close_yuan"] / I["unitree_ipo_price_yuan"], 1)

# UBTech: revenue per full-size humanoid sold (includes services)
S["ubtech_rev_per_unit_yuan_k"] = round(I["ubtech_rev_yuan_m_2025"] * 1000 / I["ubtech_units_2025"], 0)
S["ubtech_rev_growth_x"] = round(I["ubtech_rev_yuan_m_2025"] / I["ubtech_rev_yuan_m_2024"], 0)

# Agility: who paid, how much work, how much the adviser kept
S["agility_related_pct_2025"] = round(100 * I["agility_related_2025_usd_k"] / I["agility_sales_2025_usd_k"], 0)
S["agility_worker_years"] = round(I["agility_hours"] / I["full_time_hours_year"], 1)
S["agility_adviser_pct"] = round(100 * I["agility_adviser_2030"] / I["agility_pipeline_2030"], 0)
S["agility_loss_per_dollar_h1_2026"] = round(I["agility_net_loss_h1_2026_usd_m"] * 1000 / I["agility_sales_h1_2026_usd_k"], 0)
S["agility_investor_pct_2025"] = round(100 * I["agility_investor_robots_2025_usd_k"] / I["agility_sales_2025_usd_k"], 0)
S["agility_investor_pct_of_related_2025"] = round(100 * I["agility_investor_robots_2025_usd_k"] / I["agility_related_2025_usd_k"], 0)
S["agility_loss_jump_h1_2026_usd_m"] = round(I["agility_net_loss_h1_2026_usd_m"] - I["agility_net_loss_h1_2025_usd_m"], 1)
S["agility_sbc_share_of_jump_pct"] = round(100 * I["agility_sbc_increase_h1_2026_usd_m"] / S["agility_loss_jump_h1_2026_usd_m"], 0)
S["agility_loss_multiple_h1"] = round(I["agility_net_loss_h1_2026_usd_m"] / I["agility_net_loss_h1_2025_usd_m"], 1)
# Nine months to 30 Sep 2026 (8-K/A of 13 Nov 2026): the newest numbers, used in the article
S["agility_loss_jump_9m_2026_usd_m"] = round(I["agility_net_loss_9m_2026_usd_m"] - I["agility_net_loss_9m_2025_usd_m"], 1)
S["agility_sbc_share_of_jump_9m_pct"] = round(100 * I["agility_sbc_increase_9m_2026_usd_m"] / S["agility_loss_jump_9m_2026_usd_m"], 0)
S["agility_loss_multiple_9m"] = round(I["agility_net_loss_9m_2026_usd_m"] / I["agility_net_loss_9m_2025_usd_m"], 1)
S["agility_sales_drop_9m_pct"] = round(100 * (1 - I["agility_sales_9m_2026_usd_k"] / I["agility_sales_9m_2025_usd_k"]), 0)

# What the filings cover: units sold by the three makers whose filings split or describe use, vs the 2025 world range
S["filings_units_2025"] = I["unitree_units_sold"]["2025"] + I["ubtech_units_2025"] + I["leju_kuavo_units_2025"]
S["filings_coverage_pct_low"] = round(100 * S["filings_units_2025"] / I["shipments_2025_high"], 0)
S["filings_coverage_pct_high"] = round(100 * S["filings_units_2025"] / I["shipments_2025_low"], 0)

# IDC's split by use (units): labs/classrooms, shows and government data-collection centres vs everything else
S["idc_other_uses_h1_2026_pct"] = round(100 - I["idc_uses_lab_show_gov_h1_2026_pct"], 1)
S["idc_other_uses_2025_pct"] = round(100 - I["idc_uses_lab_show_gov_2025_pct"], 1)
S["idc_lab_show_gov_h1_2026_units"] = int(round(I["idc_h1_2026_units"] * I["idc_uses_lab_show_gov_h1_2026_pct"] / 100, -3))
S["idc_other_uses_h1_2026_units"] = I["idc_h1_2026_units"] - S["idc_lab_show_gov_h1_2026_units"]

# Figure at BMW: hours in worker-years, minutes per car
S["figure_bmw_worker_year_fraction"] = round(I["figure_bmw_hours"] / I["full_time_hours_year"], 2)
S["figure_bmw_minutes_per_car"] = round(I["figure_bmw_hours"] * 60 / I["figure_bmw_cars"], 1)
S["figure_bmw_parts_per_car"] = round(I["figure_bmw_parts"] / I["figure_bmw_cars"], 1)

# Capacity the makers themselves announced vs what the world ships
cap = {"Tesla (Fremont line, planned)": I["tesla_capacity"], "Hyundai (by 2028)": I["hyundai_capacity_2028"],
       "Figure (BotQ first line)": I["figure_capacity"], "Agility (RoboFab)": I["agility_robofab_capacity"],
       "UBTech (end-2025, built)": I["ubtech_capacity_2025"]}
S["capacity_rows"] = [[k, v] for k, v in cap.items()]
S["capacity_sum"] = sum(cap.values())
S["capacity_sum_ex_tesla"] = S["capacity_sum"] - I["tesla_capacity"]
S["shipments_h1_2026_annualised"] = 2 * I["idc_h1_2026_units"]
S["capacity_vs_shipments_x"] = round(S["capacity_sum"] / S["shipments_h1_2026_annualised"], 0)
S["tesla_share_of_capacity_pct"] = round(100 * I["tesla_capacity"] / S["capacity_sum"], 0)
S["idc_h1_2025_units"] = round(I["idc_h1_2026_units"] / (1 + I["idc_h1_2026_growth_pct"] / 100), -2)
S["rest_of_world_h1_2026"] = I["idc_h1_2026_units"] - I["idc_h1_2026_china_units"]

# Scale against people
S["idc_2030_pct_of_factory_workers"] = round(100 * I["idc_2030_units"] / I["ilo_manufacturing_workers"], 2)
S["factory_workers_per_2030_humanoid"] = round(I["ilo_manufacturing_workers"] / I["idc_2030_units"], 0)

# Dollars (illustrative, one rate)
r = I["usd_per_yuan"]
S["unitree_asp_2025_usd_k"] = round(S["unitree_asp_yuan_k"]["2025"] * r, 0)
S["ubtech_rev_per_unit_usd_k"] = round(S["ubtech_rev_per_unit_yuan_k"] * r, 0)
S["unitree_ipo_raised_usd_bn"] = round(I["unitree_ipo_raised_yuan_bn"] * r, 1)

json.dump(S, open(os.path.join(root, "data", "summary.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for k in ["unitree_asp_yuan_k", "unitree_work_pct_low", "unitree_work_pct_high", "unitree_tours_pct_low", "unitree_tours_pct_high",
          "ubtech_rev_per_unit_yuan_k", "agility_related_pct_2025", "agility_worker_years", "agility_adviser_pct",
          "figure_bmw_worker_year_fraction", "figure_bmw_minutes_per_car", "capacity_sum", "capacity_sum_ex_tesla",
          "capacity_vs_shipments_x", "tesla_share_of_capacity_pct", "idc_h1_2025_units", "rest_of_world_h1_2026",
          "idc_2030_pct_of_factory_workers", "factory_workers_per_2030_humanoid", "unitree_drop_from_debut_pct",
          "unitree_sep9_vs_ipo_x", "agility_loss_per_dollar_h1_2026", "unitree_asp_2025_usd_k", "ubtech_rev_per_unit_usd_k",
          "agility_investor_pct_2025", "agility_investor_pct_of_related_2025", "agility_loss_jump_h1_2026_usd_m",
          "agility_sbc_share_of_jump_pct", "agility_loss_multiple_h1", "filings_units_2025", "filings_coverage_pct_low",
          "filings_coverage_pct_high", "idc_other_uses_h1_2026_pct", "idc_other_uses_2025_pct",
          "idc_lab_show_gov_h1_2026_units", "idc_other_uses_h1_2026_units", "figure_bmw_parts_per_car",
          "agility_loss_jump_9m_2026_usd_m", "agility_sbc_share_of_jump_9m_pct", "agility_loss_multiple_9m",
          "agility_sales_drop_9m_pct"]:
    print(k, S[k])
