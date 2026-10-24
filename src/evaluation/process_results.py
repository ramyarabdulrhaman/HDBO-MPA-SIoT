"""
Statistical Results Processor and Table Generator for HDBO-MPA Research.
Parses raw CSV benchmark records, computes descriptive statistics (Mean, Std, Median, IQR),
executes Wilcoxon signed-rank tests with Holm-Bonferroni correction, Friedman tests,
Nemenyi post-hoc Critical Differences, Bootstrap 95% Confidence Intervals,
and generates publication-ready Markdown and CSV tables for the manuscript.
"""

import os
import sys
import csv
import json
import numpy as np

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.evaluation.statistical_tests import (
    compute_wilcoxon_signed_rank, apply_holm_bonferroni_correction,
    compute_friedman_test, compute_bootstrap_ci, compute_nemenyi_critical_difference
)

def process_benchmark_results(raw_csv, tables_dir):
    """
    Processes Experiment 1A multi-objective benchmark results across 30 independent runs on SNAP ego-Facebook.
    """
    if not os.path.exists(raw_csv):
        print(f"File not found: {raw_csv}")
        return
        
    records = []
    with open(raw_csv, "r") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append(r)
            
    algorithms = [
        "HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", 
        "MOEA/D", "SPEA2", "MOMPA", "ACO", "T-Greedy", "Dijkstra"
    ]
    metrics = [
        "hypervolume", "igd_plus", "spacing", "best_trust", 
        "best_latency", "best_energy", "best_qos", "best_hops", 
        "runtime_sec", "eval_count", "constraint_violation", "path_feasible"
    ]
    
    data_by_alg = {alg: {m: [] for m in metrics} for alg in algorithms}
    for r in records:
        alg = r["algorithm"]
        if alg in data_by_alg:
            for m in metrics:
                data_by_alg[alg][m].append(float(r[m]))
                
    # 1. Generate Table 1: Multi-Objective Comparative Summary (Mean +/- Std, Median [IQR])
    summary_rows = []
    for alg in algorithms:
        if not data_by_alg[alg]["hypervolume"]:
            continue
        row = {"Algorithm": alg}
        for m in metrics:
            vals = np.array(data_by_alg[alg][m])
            mean_v = np.mean(vals)
            std_v = np.std(vals)
            med_v = np.median(vals)
            q25, q75 = np.percentile(vals, [25, 75])
            iqr_v = q75 - q25
            
            row[f"{m}_mean_std"] = f"{mean_v:.4f} ± {std_v:.4f}"
            row[f"{m}_median_iqr"] = f"{med_v:.4f} [{iqr_v:.4f}]"
            row[f"{m}_mean"] = mean_v
            row[f"{m}_std"] = std_v
        summary_rows.append(row)
        
    tbl1_csv = os.path.join(tables_dir, "table_1_multiobjective_summary.csv")
    with open(tbl1_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
        
    tbl1_md = os.path.join(tables_dir, "table_1_multiobjective_summary.md")
    with open(tbl1_md, "w", encoding="utf-8") as f:
        f.write("# Table I: Multi-Objective Performance Benchmarking Across 30 Independent Runs (SNAP ego-Facebook, N=250)\n\n")
        f.write("| Algorithm | Hypervolume (HV) ↑ | IGD+ ↓ | Spacing (S) ↓ | Composite Trust ↑ | Latency (ms) ↓ | Energy (mJ) ↓ | QoS Index ↑ | Feasibility (%) | Runtime (s) ↓ |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for r in summary_rows:
            feas_pct = r["path_feasible_mean"] * 100.0
            f.write(f"| **{r['Algorithm']}** | {r['hypervolume_mean_std']} | {r['igd_plus_mean_std']} | {r['spacing_mean_std']} | {r['best_trust_mean_std']} | {r['best_latency_mean_std']} | {r['best_energy_mean_std']} | {r['best_qos_mean_std']} | {feas_pct:.1f}% | {r['runtime_sec_mean_std']} |\n")
            
    print(f"Generated Table 1 in {tbl1_md}")
    
    # 2. Pairwise Wilcoxon Signed-Rank Tests vs HDBO-MPA on Hypervolume (with Bootstrap 95% CIs)
    hdbo_hv = data_by_alg["HDBO-MPA"]["hypervolume"]
    wilcox_results = []
    p_vals_dict = {}
    
    for alg in algorithms:
        if alg == "HDBO-MPA" or not data_by_alg[alg]["hypervolume"]:
            continue
        comp_hv = data_by_alg[alg]["hypervolume"]
        res = compute_wilcoxon_signed_rank(hdbo_hv, comp_hv)
        boot_ci = compute_bootstrap_ci(hdbo_hv, comp_hv)
        p_vals_dict[alg] = res["p_value"]
        wilcox_results.append({
            "Baseline": alg,
            "Statistic_W": res["statistic"],
            "Z_Score": res["z_score"],
            "Raw_p_value": res["p_value"],
            "Effect_Size_r": res["effect_size_r"],
            "Mean_Diff": boot_ci["mean_diff"],
            "Mean_CI_95": f"[{boot_ci['mean_ci_95'][0]:.4f}, {boot_ci['mean_ci_95'][1]:.4f}]",
            "Median_Diff": boot_ci["median_diff"],
            "Median_CI_95": f"[{boot_ci['median_ci_95'][0]:.4f}, {boot_ci['median_ci_95'][1]:.4f}]"
        })
        
    holm_results = apply_holm_bonferroni_correction(p_vals_dict, alpha=0.05)
    for wr in wilcox_results:
        alg = wr["Baseline"]
        wr["Adjusted_Alpha"] = holm_results[alg]["adjusted_alpha"]
        wr["Significant_After_Correction"] = holm_results[alg]["significant_after_correction"]
        
    tbl2_md = os.path.join(tables_dir, "table_2_wilcoxon_statistical_tests.md")
    with open(tbl2_md, "w", encoding="utf-8") as f:
        f.write("# Table II: Pairwise Wilcoxon Signed-Rank Test with Holm-Bonferroni Correction & Bootstrap 95% CIs (Hypervolume)\n\n")
        f.write("| Comparison | W Stat | Z-Score | Raw $p$-value | Adjusted $\\alpha$ | Effect Size ($r$) | Mean Diff (95% CI) | Statistically Significant? |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for wr in wilcox_results:
            sig_txt = "Yes ($p < \\alpha_{adj}$)" if wr["Significant_After_Correction"] else "No"
            f.write(f"| HDBO-MPA vs. **{wr['Baseline']}** | {wr['Statistic_W']:.1f} | {wr['Z_Score']:.3f} | {wr['Raw_p_value']:.4e} | {wr['Adjusted_Alpha']:.4f} | {wr['Effect_Size_r']:.3f} | {wr['Mean_Diff']:+.4f} {wr['Mean_CI_95']} | **{sig_txt}** |\n")
            
    tbl2_csv = os.path.join(tables_dir, "table_2_wilcoxon_statistical_tests.csv")
    with open(tbl2_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(wilcox_results[0].keys()))
        writer.writeheader()
        writer.writerows(wilcox_results)
    print(f"Generated Table 2 in {tbl2_md}")
    
    # 3. Friedman Test & Nemenyi Critical Difference
    active_algs = [a for a in algorithms if data_by_alg[a]["hypervolume"]]
    friedman_data = {alg: data_by_alg[alg]["hypervolume"] for alg in active_algs}
    friedman_res = compute_friedman_test(friedman_data)
    num_runs = len(data_by_alg["HDBO-MPA"]["hypervolume"])
    cd_val = compute_nemenyi_critical_difference(len(active_algs), num_runs, alpha=0.05)
    
    tbl3_md = os.path.join(tables_dir, "table_3_friedman_ranks.md")
    with open(tbl3_md, "w", encoding="utf-8") as f:
        f.write("# Table III: Friedman Non-Parametric Test, Average Algorithm Rankings, and Nemenyi Critical Difference\n\n")
        f.write(f"- **Friedman $\\chi_F^2$ Statistic:** {friedman_res['chi2_statistic']:.4f}\n")
        f.write(f"- **Degrees of Freedom (df):** {friedman_res['degrees_of_freedom']}\n")
        f.write(f"- **Asymptotic $p$-value:** {friedman_res['p_value']:.4e}\n")
        f.write(f"- **Statistical Significance:** {'Statistically Significant ($p < 0.05$)' if friedman_res['significant'] else 'Not Significant'}\n")
        f.write(f"- **Nemenyi Critical Difference ($CD$ at $\\alpha = 0.05$):** **{cd_val:.4f}**\n\n")
        f.write("| Overall Rank | Algorithm | Average Rank (Lower is Superior) | Significant vs Top Rank? (Diff > CD) |\n")
        f.write("|---|---|---|---|\n")
        sorted_ranks = sorted(friedman_res["average_ranks"].items(), key=lambda x: x[1])
        top_rank_val = sorted_ranks[0][1]
        for rank_num, (alg_name, avg_r) in enumerate(sorted_ranks, 1):
            diff_from_top = avg_r - top_rank_val
            sig_vs_top = f"Yes (Δ = {diff_from_top:.2f} > CD)" if diff_from_top > cd_val else "No (Statistically Indistinguishable)"
            f.write(f"| Rank #{rank_num} | **{alg_name}** | {avg_r:.2f} | {sig_vs_top} |\n")
            
    print(f"Generated Table 3 in {tbl3_md}")

def process_scale_free_results(raw_csv, tables_dir):
    """
    Processes secondary benchmark on Barabasi-Albert scale-free graph.
    """
    if not os.path.exists(raw_csv):
        return
        
    records = []
    with open(raw_csv, "r") as f:
        for r in csv.DictReader(f):
            records.append(r)
            
    algs = sorted(list(set(r["algorithm"] for r in records)))
    summary_rows = []
    
    for alg in algs:
        alg_recs = [r for r in records if r["algorithm"] == alg]
        hvs = [float(r["hypervolume"]) for r in alg_recs]
        igds = [float(r["igd_plus"]) for r in alg_recs]
        spacings = [float(r["spacing"]) for r in alg_recs]
        trusts = [float(r["best_trust"]) for r in alg_recs]
        lats = [float(r["best_latency"]) for r in alg_recs]
        energies = [float(r["best_energy"]) for r in alg_recs]
        
        summary_rows.append({
            "Algorithm": alg,
            "HV": f"{np.mean(hvs):.4f} ± {np.std(hvs):.4f}",
            "IGD+": f"{np.mean(igds):.4f} ± {np.std(igds):.4f}",
            "Spacing": f"{np.mean(spacings):.4f} ± {np.std(spacings):.4f}",
            "Trust": f"{np.mean(trusts):.4f} ± {np.std(trusts):.4f}",
            "Latency": f"{np.mean(lats):.2f} ± {np.std(lats):.2f}",
            "Energy": f"{np.mean(energies):.2f} ± {np.std(energies):.2f}"
        })
        
    tbl7_md = os.path.join(tables_dir, "table_7_scale_free_benchmark.md")
    with open(tbl7_md, "w", encoding="utf-8") as f:
        f.write("# Table VII: Secondary Benchmark Performance on Barabási-Albert Scale-Free Topology ($N=250$, 30 Runs)\n\n")
        f.write("| Algorithm | Hypervolume (HV) ↑ | IGD+ ↓ | Spacing (S) ↓ | Composite Trust ↑ | Latency (ms) ↓ | Energy (mJ) ↓ |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in summary_rows:
            f.write(f"| **{r['Algorithm']}** | {r['HV']} | {r['IGD+']} | {r['Spacing']} | {r['Trust']} | {r['Latency']} | {r['Energy']} |\n")
            
    print(f"Generated Table 7 in {tbl7_md}")

def process_attack_results(attack_csv, tables_dir):
    """
    Processes Experiment 2 attack resilience data across malicious ratios (10-60%) and attack modes.
    """
    if not os.path.exists(attack_csv):
        return
        
    records = []
    with open(attack_csv, "r") as f:
        for r in csv.DictReader(f):
            records.append(r)
            
    tbl4_md = os.path.join(tables_dir, "table_4_attack_resilience.md")
    with open(tbl4_md, "w", encoding="utf-8") as f:
        f.write("# Table IV: Multi-Model Adversarial Resilience Across Malicious Proportions (10%–60%)\n\n")
        f.write("| Malicious Ratio (%) | Attack Mode | SDSR-A (%) | True Delivery (%) | Malicious Relay Frac (%) | Proposed F1 | Proposed FAR | Beta-Rep F1 | Beta-Rep FAR | EigenTrust F1 | EigenTrust FAR |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
        for r in records:
            ratio_pct = int(float(r["malicious_ratio"]) * 100)
            sdsr_pct = float(r["sdsr_a"]) * 100
            td_pct = float(r["true_delivery_rate"]) * 100
            mal_frac_pct = float(r["avg_malicious_path_fraction"]) * 100
            mode = r["attack_mode"]
            
            f.write(f"| {ratio_pct}% | {mode} | **{sdsr_pct:.1f}%** | {td_pct:.1f}% | {mal_frac_pct:.1f}% | **{float(r['prop_f1']):.4f}** | **{float(r['prop_far']):.4f}** | {float(r['beta_f1']):.4f} | {float(r['beta_far']):.4f} | {float(r['eigen_f1']):.4f} | {float(r['eigen_far']):.4f} |\n")
            
    print(f"Generated Table 4 in {tbl4_md}")

def process_scalability_results(sc_csv, tables_dir):
    """
    Processes Experiment 3 scalability data.
    """
    if not os.path.exists(sc_csv):
        return
        
    records = []
    with open(sc_csv, "r") as f:
        for r in csv.DictReader(f):
            records.append(r)
            
    tbl5_md = os.path.join(tables_dir, "table_5_scalability.md")
    with open(tbl5_md, "w", encoding="utf-8") as f:
        f.write("# Table V: Scalability Across Network Topologies ($N = 100$ to $1000$ Nodes)\n\n")
        f.write("| Nodes ($|V|$) | Edges ($|E|$) | Algorithm | Runtime (s) | Evaluations | Hypervolume (HV) | Path Latency (ms) | Path Energy (mJ) |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in records:
            f.write(f"| {r['nodes']} | {r['edges']} | **{r['algorithm']}** | {float(r['runtime_sec']):.2f}s | {r['eval_count']} | {float(r['hypervolume']):.4f} | {float(r['latency']):.1f} | {float(r['energy']):.2f} |\n")
            
    print(f"Generated Table 5 in {tbl5_md}")

def process_ablation_results(abl_csv, tables_dir):
    """
    Processes Experiment 4 ablation study data across 10 runs for variants A0 to A10.
    """
    if not os.path.exists(abl_csv):
        return
        
    records = []
    with open(abl_csv, "r") as f:
        for r in csv.DictReader(f):
            records.append(r)
            
    codes = [
        "A0_Full_HDBO_MPA", "A1_DBO_Only", "A2_MPA_Only", "A3_No_Entropy_Weighting",
        "A4_Direct_Trust_Only", "A5_No_Social_Relationship", "A6_No_Indirect_Trust",
        "A7_Sequential_Hybrid", "A8_Random_Selection", "A9_No_Loop_Erasure", "A10_No_Archive_Crowding"
    ]
    
    summary = []
    for code in codes:
        recs = [r for r in records if r["ablation_code"] == code]
        if not recs:
            continue
        hvs = [float(r["hypervolume"]) for r in recs]
        sizes = [int(r["pareto_size"]) for r in recs]
        trusts = [float(r["trust"]) for r in recs]
        lats = [float(r["latency"]) for r in recs]
        energies = [float(r["energy"]) for r in recs]
        qoses = [float(r["qos"]) for r in recs]
        loops = [float(r["has_loop"]) for r in recs]
        
        summary.append({
            "code": code,
            "hv_mean": np.mean(hvs),
            "hv_std": np.std(hvs),
            "pareto_size": f"{np.mean(sizes):.1f}",
            "trust": f"{np.mean(trusts):.3f}",
            "latency": f"{np.mean(lats):.1f}",
            "energy": f"{np.mean(energies):.2f}",
            "qos": f"{np.mean(qoses):.3f}",
            "loop_freq": f"{np.mean(loops)*100.0:.1f}%"
        })
        
    tbl6_md = os.path.join(tables_dir, "table_6_ablation_study.md")
    with open(tbl6_md, "w", encoding="utf-8") as f:
        f.write("# Table VI: Systematic Component Ablation Study (Variants A0 Through A10, 10 Runs Each)\n\n")
        f.write("| Variant Code | Description | Hypervolume (HV) | Pareto Front Size | Trust Score | Latency (ms) | Energy (mJ) | QoS Index | Cycle/Loop Frequency (%) |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for s in summary:
            f.write(f"| **{s['code']}** | Model Variant | **{s['hv_mean']:.4f} ± {s['hv_std']:.4f}** | {s['pareto_size']} | {s['trust']} | {s['latency']} | {s['energy']} | {s['qos']} | **{s['loop_freq']}** |\n")
            
    tbl6_csv = os.path.join(tables_dir, "table_6_ablation_study.csv")
    with open(tbl6_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    print(f"Generated Table 6 in {tbl6_md}")

def process_all():
    tables_dir = os.path.join(root_dir, "tables")
    raw_dir = os.path.join(root_dir, "experiments", "raw_results")
    os.makedirs(tables_dir, exist_ok=True)
    
    bench_csv = os.path.join(raw_dir, "multi_objective_benchmark_raw.csv")
    sec_csv = os.path.join(raw_dir, "secondary_dataset_benchmark_raw.csv")
    attack_csv = os.path.join(raw_dir, "attack_resilience_raw.csv")
    sc_csv = os.path.join(raw_dir, "scalability_raw.csv")
    abl_csv = os.path.join(raw_dir, "ablation_study_raw.csv")
    
    process_benchmark_results(bench_csv, tables_dir)
    process_scale_free_results(sec_csv, tables_dir)
    process_attack_results(attack_csv, tables_dir)
    process_scalability_results(sc_csv, tables_dir)
    process_ablation_results(abl_csv, tables_dir)
    print("\nAll publication summary tables successfully processed and generated.")

if __name__ == "__main__":
    process_all()
