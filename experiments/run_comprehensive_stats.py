"""
Comprehensive Statistical Testing and Table Regeneration Engine.
Evaluates multi-objective discovery, adversarial resilience, scalability, and ablation.
Strictly reports authentic metrics from raw logs with zero invention or adjustments.
"""

import os
import csv
import math
import numpy as np
import pandas as pd
from scipy import stats

def compute_bootstrap_ci(data, num_bootstraps=2000, alpha=0.05):
    """Computes non-parametric bootstrap 95% confidence interval for the mean."""
    n = len(data)
    if n == 0:
        return 0.0, 0.0
    boot_means = []
    rng = np.random.RandomState(42)
    for _ in range(num_bootstraps):
        sample = rng.choice(data, size=n, replace=True)
        boot_means.append(np.mean(sample))
    low = np.percentile(boot_means, 100 * (alpha / 2.0))
    high = np.percentile(boot_means, 100 * (1.0 - alpha / 2.0))
    return float(low), float(high)

def process_benchmarks(root_dir):
    raw_dir = os.path.join(root_dir, "experiments", "raw_results")
    tables_dir = os.path.join(root_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)
    
    # =========================================================================
    # 1. Multi-Objective Benchmark on SNAP-250 (11 Algorithms, 30 Runs)
    # =========================================================================
    csv_1a = os.path.join(raw_dir, "multi_objective_benchmark_raw.csv")
    if os.path.exists(csv_1a):
        print(f"Loading {csv_1a}...")
        df1 = pd.read_csv(csv_1a)
        
        algorithms = [
            "HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", 
            "MOEA/D", "SPEA2", "MOMPA", "ACO", "T-Greedy", "Dijkstra"
        ]
        
        # Table 1: Summary Statistics
        t1_rows = []
        for alg in algorithms:
            sub = df1[df1["algorithm"] == alg]
            if sub.empty:
                continue
            hv = sub["hypervolume"].values
            igd = sub["igd_plus"].values
            sp = sub["spacing"].values
            tr = sub["best_trust"].values
            lat = sub["best_latency"].values
            eng = sub["best_energy"].values
            qos = sub["best_qos"].values
            feas = sub["path_feasible"].values
            rt = sub["runtime_sec"].values
            
            t1_rows.append({
                "Algorithm": f"**{alg}**" if alg == "HDBO-MPA" else alg,
                "Hypervolume (HV) ↑": f"{np.mean(hv):.4f} ± {np.std(hv):.4f}",
                "IGD+ ↓": f"{np.mean(igd):.4f} ± {np.std(igd):.4f}",
                "Spacing (S) ↓": f"{np.mean(sp):.4f} ± {np.std(sp):.4f}",
                "Composite Trust ↑": f"{np.mean(tr):.4f} ± {np.std(tr):.4f}",
                "Latency (ms) ↓": f"{np.mean(lat):.4f} ± {np.std(lat):.4f}",
                "Energy (mJ) ↓": f"{np.mean(eng):.4f} ± {np.std(eng):.4f}",
                "QoS Index ↑": f"{np.mean(qos):.4f} ± {np.std(qos):.4f}",
                "Feasibility (%)": f"{np.mean(feas)*100:.1f}%",
                "Runtime (s) ↓": f"{np.mean(rt):.4f} ± {np.std(rt):.4f}"
            })
            
        t1_df = pd.DataFrame(t1_rows)
        t1_md = os.path.join(tables_dir, "table_1_multiobjective_summary.md")
        with open(t1_md, "w", encoding="utf-8") as f:
            f.write("# Table I: Multi-Objective Performance Benchmarking Across 30 Independent Runs (SNAP ego-Facebook, N=250)\n\n")
            f.write(t1_df.to_markdown(index=False))
            f.write("\n")
        print(f"Generated {t1_md}")
        
        # Table 2: Pairwise Wilcoxon Signed-Rank Tests vs. HDBO-MPA (HV)
        hdbo_hv = df1[df1["algorithm"] == "HDBO-MPA"]["hypervolume"].values
        baselines = [a for a in algorithms if a != "HDBO-MPA"]
        
        w_records = []
        for b in baselines:
            b_hv = df1[df1["algorithm"] == b]["hypervolume"].values
            diff = hdbo_hv - b_hv
            mean_diff = float(np.mean(diff))
            ci_low, ci_high = compute_bootstrap_ci(diff)
            
            nonzero = diff[diff != 0]
            n = len(nonzero)
            if n > 0:
                res = stats.wilcoxon(hdbo_hv, b_hv, zero_method='wilcox', correction=True)
                w_stat = float(res.statistic)
                p_val = float(res.pvalue)
                mean_w = n * (n + 1) / 4.0
                var_w = n * (n + 1) * (2 * n + 1) / 24.0
                z_score = float((w_stat - mean_w) / np.sqrt(var_w)) if var_w > 0 else 0.0
                r = float(abs(z_score) / np.sqrt(n))
            else:
                w_stat, p_val, z_score, r = 0.0, 1.0, 0.0, 0.0
                
            w_records.append({
                "baseline": b,
                "w_stat": w_stat,
                "z_score": z_score,
                "raw_p": p_val,
                "effect_size_r": r,
                "mean_diff": mean_diff,
                "ci_low": ci_low,
                "ci_high": ci_high
            })
            
        # Holm-Bonferroni correction
        w_records = sorted(w_records, key=lambda x: x["raw_p"])
        m = len(w_records)
        t2_rows = []
        for k, rec in enumerate(w_records, 1):
            alpha_adj = 0.05 / (m - k + 1)
            sig = rec["raw_p"] < alpha_adj
            
            # State explicit direction of significance
            if sig:
                if rec["mean_diff"] > 0:
                    sig_label = "**Yes (HDBO-MPA > Baseline, p < alpha_adj)**"
                else:
                    sig_label = f"**Yes ({rec['baseline']} > HDBO-MPA, p < alpha_adj)**"
            else:
                sig_label = "No (Indistinguishable)"
                
            sign_str = "+" if rec["mean_diff"] >= 0 else ""
            t2_rows.append({
                "Comparison": f"HDBO-MPA vs. **{rec['baseline']}**",
                "W Stat": f"{rec['w_stat']:.1f}",
                "Z-Score": f"{rec['z_score']:.3f}",
                "Raw $p$-value": f"{rec['raw_p']:.4e}",
                "Adjusted $\\alpha$": f"{alpha_adj:.4f}",
                "Rank-Biserial ($r$)": f"{rec['effect_size_r']:.3f}",
                "Mean Diff (95% CI)": f"{sign_str}{rec['mean_diff']:.4f} [{rec['ci_low']:.4f}, {rec['ci_high']:.4f}]",
                "Statistically Significant?": sig_label
            })
            
        t2_df = pd.DataFrame(t2_rows)
        t2_md = os.path.join(tables_dir, "table_2_wilcoxon_statistical_tests.md")
        with open(t2_md, "w", encoding="utf-8") as f:
            f.write("# Table II: Pairwise Wilcoxon Signed-Rank Test with Holm-Bonferroni Correction & Bootstrap 95% CIs (Hypervolume)\n\n")
            f.write(t2_df.to_markdown(index=False))
            f.write("\n")
        print(f"Generated {t2_md}")
        
        # Table 3: Friedman Test & Nemenyi Critical Difference (k=11, df=10)
        hv_matrix = np.column_stack([df1[df1["algorithm"] == a]["hypervolume"].values for a in algorithms])
        chi2_f, p_f = stats.friedmanchisquare(*[hv_matrix[:, i] for i in range(len(algorithms))])
        
        # Rank: higher HV is better -> rank 1
        ranks = np.zeros_like(hv_matrix)
        for i in range(len(hv_matrix)):
            ranks[i] = stats.rankdata(-hv_matrix[i])
        avg_ranks = np.mean(ranks, axis=0)
        
        k_algs = len(algorithms)
        n_runs = len(hv_matrix)
        # Nemenyi critical value q_alpha at alpha=0.05 for k=11 is 3.219
        q_alpha = 3.219
        nemenyi_cd = q_alpha * math.sqrt((k_algs * (k_algs + 1)) / (6.0 * n_runs))
        
        sorted_algs = sorted(zip(algorithms, avg_ranks), key=lambda x: x[1])
        best_rank = sorted_algs[0][1]
        
        t3_rows = []
        for rank_idx, (a, rk) in enumerate(sorted_algs, 1):
            diff_from_best = rk - best_rank
            sig_vs_best = "Yes (Δ > CD)" if diff_from_best > nemenyi_cd else "No (Statistically Indistinguishable)"
            t3_rows.append({
                "Overall Rank": f"Rank #{rank_idx}",
                "Algorithm": f"**{a}**" if a == "HDBO-MPA" else a,
                "Average Rank (Lower is Superior)": f"{rk:.2f}",
                "Significant vs Top Rank? (Diff > CD)": sig_vs_best
            })
            
        t3_df = pd.DataFrame(t3_rows)
        t3_md = os.path.join(tables_dir, "table_3_friedman_ranks.md")
        with open(t3_md, "w", encoding="utf-8") as f:
            f.write("# Table III: Friedman Non-Parametric Test, Average Algorithm Rankings, and Nemenyi Critical Difference\n\n")
            f.write(f"- **Friedman $\\chi_F^2$ Statistic:** {chi2_f:.4f}\n")
            f.write(f"- **Degrees of Freedom (df):** {k_algs - 1}\n")
            f.write(f"- **Asymptotic $p$-value:** {p_f:.4e}\n")
            f.write(f"- **Statistical Significance:** {'Statistically Significant ($p < 0.05$)' if p_f < 0.05 else 'Not Significant'}\n")
            f.write(f"- **Nemenyi Critical Difference ($CD$ at $\\alpha = 0.05$):** **{nemenyi_cd:.4f}**\n\n")
            f.write(t3_df.to_markdown(index=False))
            f.write("\n")
        print(f"Generated {t3_md}")
        
    # =========================================================================
    # 2. Secondary Benchmark on Barabási-Albert Scale-Free Graph (8 Algorithms)
    # =========================================================================
    csv_1b = os.path.join(raw_dir, "secondary_dataset_benchmark_raw.csv")
    if os.path.exists(csv_1b):
        print(f"Loading {csv_1b}...")
        df1b = pd.read_csv(csv_1b)
        algs_sf = ["HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", "MOEA/D", "SPEA2", "MOMPA"]
        
        t7_rows = []
        for alg in algs_sf:
            sub = df1b[df1b["algorithm"] == alg]
            if sub.empty:
                continue
            hv = sub["hypervolume"].values
            igd = sub["igd_plus"].values
            sp = sub["spacing"].values
            tr = sub["best_trust"].values
            lat = sub["best_latency"].values
            eng = sub["best_energy"].values
            
            t7_rows.append({
                "Algorithm": f"**{alg}**" if alg == "HDBO-MPA" else alg,
                "Hypervolume (HV) ↑": f"{np.mean(hv):.4f} ± {np.std(hv):.4f}",
                "IGD+ ↓": f"{np.mean(igd):.4f} ± {np.std(igd):.4f}",
                "Spacing (S) ↓": f"{np.mean(sp):.4f} ± {np.std(sp):.4f}",
                "Composite Trust ↑": f"{np.mean(tr):.4f} ± {np.std(tr):.4f}",
                "Latency (ms) ↓": f"{np.mean(lat):.2f} ± {np.std(lat):.2f}",
                "Energy (mJ) ↓": f"{np.mean(eng):.2f} ± {np.std(eng):.2f}"
            })
            
        t7_df = pd.DataFrame(t7_rows)
        t7_md = os.path.join(tables_dir, "table_7_scale_free_benchmark.md")
        with open(t7_md, "w", encoding="utf-8") as f:
            f.write("# Table VII: Secondary Benchmark Performance on Barabási-Albert Scale-Free Topology ($N=250$, 30 Runs)\n\n")
            f.write(t7_df.to_markdown(index=False))
            f.write("\n")
        print(f"Generated {t7_md}")

    # =========================================================================
    # 3. Adversarial Security and Attack Resilience (10% to 60%)
    # =========================================================================
    csv_2 = os.path.join(raw_dir, "attack_resilience_raw.csv")
    if os.path.exists(csv_2):
        print(f"Loading {csv_2}...")
        df2 = pd.read_csv(csv_2)
        
        t4_rows = []
        for _, row in df2.iterrows():
            r_pct = f"{int(row['malicious_ratio']*100)}%"
            t4_rows.append({
                "Malicious Ratio (%)": r_pct,
                "Attack Mode": row["attack_mode"],
                "SDSR-A (%)": f"{row['sdsr_a']*100:.1f}%",
                "True Delivery (%)": f"{row['true_delivery_rate']*100:.1f}%",
                "Malicious Relay Frac (%)": f"{row['avg_malicious_path_fraction']*100:.1f}%",
                "Proposed F1": f"{row['prop_f1']:.4f}",
                "Proposed FAR": f"{row['prop_far']:.4f}",
                "Beta-Rep F1": f"{row['beta_f1']:.4f}",
                "Beta-Rep FAR": f"{row['beta_far']:.4f}",
                "EigenTrust F1": f"{row['eigen_f1']:.4f}",
                "EigenTrust FAR": f"{row['eigen_far']:.4f}"
            })
            
        t4_df = pd.DataFrame(t4_rows)
        t4_md = os.path.join(tables_dir, "table_4_attack_resilience.md")
        with open(t4_md, "w", encoding="utf-8") as f:
            f.write("# Table IV: Multi-Model Adversarial Resilience Across Malicious Proportions (10%–60%)\n\n")
            f.write(t4_df.to_markdown(index=False))
            f.write("\n")
        print(f"Generated {t4_md}")

    # =========================================================================
    # 4. Scalability Across Topologies (N=100 to 1000 Nodes)
    # =========================================================================
    csv_3 = os.path.join(raw_dir, "scalability_raw.csv")
    if os.path.exists(csv_3):
        print(f"Loading {csv_3}...")
        df3 = pd.read_csv(csv_3)
        
        t5_rows = []
        for _, row in df3.iterrows():
            t5_rows.append({
                "Nodes ($|V|$)": int(row["nodes"]),
                "Edges ($|E|$)": int(row["edges"]),
                "Algorithm": f"**{row['algorithm']}**" if row['algorithm'] == 'HDBO-MPA' else row['algorithm'],
                "Runtime (s)": f"{row['runtime_sec']:.2f}s",
                "Evaluations": int(row["eval_count"]),
                "Hypervolume (HV)": f"{row['hypervolume']:.4f}",
                "Path Latency (ms)": f"{row['latency']:.1f}",
                "Path Energy (mJ)": f"{row['energy']:.2f}"
            })
            
        t5_df = pd.DataFrame(t5_rows)
        t5_md = os.path.join(tables_dir, "table_5_scalability.md")
        with open(t5_md, "w", encoding="utf-8") as f:
            f.write("# Table V: Scalability Across Network Topologies ($N = 100$ to $1000$ Nodes)\n\n")
            f.write(t5_df.to_markdown(index=False))
            f.write("\n")
        print(f"Generated {t5_md}")

    # =========================================================================
    # 5. Systematic Component Ablation Study (30 Runs, A0 to A10)
    # =========================================================================
    csv_4 = os.path.join(raw_dir, "ablation_study_raw.csv")
    if os.path.exists(csv_4):
        print(f"Loading {csv_4}...")
        df4 = pd.read_csv(csv_4)
        
        ablations = [
            ("A0_Full_HDBO_MPA", "Full Proposed Model"),
            ("A1_DBO_Only", "DBO Sub-Population Only"),
            ("A2_MPA_Only", "MPA Sub-Population Only"),
            ("A3_No_Entropy_Weighting", "Uniform Recommender Weights"),
            ("A4_Direct_Trust_Only", "Excludes Indirect/Social Trust"),
            ("A5_No_Social_Relationship", "Excludes Atzori Social Ties"),
            ("A6_No_Indirect_Trust", "Excludes Recommender Feedback"),
            ("A7_Sequential_Hybrid", "Sequential DBO to MPA"),
            ("A8_Random_Selection", "Random-Key (No Heuristic Score)"),
            ("A9_No_Loop_Erasure", "Raw Traversal (No Loop-Erasure)"),
            ("A10_No_Archive_Crowding", "Random Archive Pruning")
        ]
        
        a0_hv = df4[df4["ablation_code"] == "A0_Full_HDBO_MPA"]["hypervolume"].values
        
        t6_rows = []
        for code, desc in ablations:
            sub = df4[df4["ablation_code"] == code]
            if sub.empty:
                continue
            hv = sub["hypervolume"].values
            ps = sub["pareto_size"].values
            tr = sub["trust"].values
            lat = sub["latency"].values
            eng = sub["energy"].values
            qos = sub["qos"].values
            has_loop = sub["has_loop"].values
            
            # Paired Wilcoxon signed-rank test against A0
            if code != "A0_Full_HDBO_MPA" and len(hv) == len(a0_hv):
                diff = a0_hv - hv
                nonzero = diff[diff != 0]
                if len(nonzero) > 0:
                    res = stats.wilcoxon(a0_hv, hv, zero_method='wilcox', correction=True)
                    p_str = f"p={res.pvalue:.4f}"
                else:
                    p_str = "tied"
            else:
                p_str = "Baseline"
                
            t6_rows.append({
                "Variant Code": f"**{code}**" if code == "A0_Full_HDBO_MPA" else code,
                "Description": desc,
                "Hypervolume (HV)": f"**{np.mean(hv):.4f} ± {np.std(hv):.4f}**" if code == "A0_Full_HDBO_MPA" else f"{np.mean(hv):.4f} ± {np.std(hv):.4f}",
                "Wilcoxon vs A0": p_str,
                "Pareto Front Size": f"{np.mean(ps):.1f}",
                "Trust Score": f"{np.mean(tr):.3f}",
                "Latency (ms)": f"{np.mean(lat):.1f}",
                "Energy (mJ)": f"{np.mean(eng):.2f}",
                "QoS Index": f"{np.mean(qos):.3f}",
                "Cycle/Loop Frequency (%)": f"{np.mean(has_loop)*100:.1f}%"
            })
            
        t6_df = pd.DataFrame(t6_rows)
        t6_md = os.path.join(tables_dir, "table_6_ablation_study.md")
        with open(t6_md, "w", encoding="utf-8") as f:
            f.write("# Table VI: Systematic Component Ablation Study (Variants A0 Through A10, 30 Runs Each)\n\n")
            f.write(t6_df.to_markdown(index=False))
            f.write("\n")
        print(f"Generated {t6_md}")

    print("\nAll statistical tables successfully processed and generated.")

if __name__ == "__main__":
    process_benchmarks(".")
