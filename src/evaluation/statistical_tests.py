"""
Statistical Validation Engine for Multi-Objective Optimization Benchmarking.
Implements Wilcoxon signed-rank tests with Holm-Bonferroni correction,
Friedman non-parametric tests, post-hoc ranking, and effect size calculations.
"""

import numpy as np
from scipy import stats

def compute_wilcoxon_signed_rank(x, y):
    """
    Computes the two-sided Wilcoxon signed-rank test for paired samples.
    Returns test statistic W, p-value, and effect size r = Z / sqrt(N).
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    diff = x - y
    
    # Remove zero differences
    nonzero_diff = diff[diff != 0]
    n_pairs = len(nonzero_diff)
    if n_pairs < 5:
        return {"statistic": 0.0, "p_value": 1.0, "effect_size_r": 0.0, "significant": False}
        
    res = stats.wilcoxon(x, y, zero_method='wilcox', correction=True)
    w_stat = float(res.statistic)
    p_val = float(res.pvalue)
    
    # Compute asymptotic Z-score for effect size r
    mean_w = n_pairs * (n_pairs + 1) / 4.0
    var_w = n_pairs * (n_pairs + 1) * (2 * n_pairs + 1) / 24.0
    z_score = (w_stat - mean_w) / np.sqrt(var_w) if var_w > 0 else 0.0
    effect_size_r = float(abs(z_score) / np.sqrt(n_pairs))
    
    return {
        "statistic": w_stat,
        "p_value": p_val,
        "z_score": float(z_score),
        "effect_size_r": effect_size_r,
        "significant": p_val < 0.05
    }

def apply_holm_bonferroni_correction(p_values_dict, alpha=0.05):
    """
    Applies Holm-Bonferroni step-down procedure across multiple pairwise comparisons.
    p_values_dict: dict mapping comparison name -> raw p-value
    """
    sorted_comparisons = sorted(p_values_dict.items(), key=lambda item: item[1])
    m = len(sorted_comparisons)
    
    results = {}
    passed = True
    for k, (name, raw_p) in enumerate(sorted_comparisons, 1):
        adjusted_alpha = alpha / (m - k + 1)
        if passed and raw_p <= adjusted_alpha:
            is_sig = True
        else:
            is_sig = False
            passed = False
            
        results[name] = {
            "rank": k,
            "raw_p": float(raw_p),
            "adjusted_alpha": float(adjusted_alpha),
            "significant_after_correction": is_sig
        }
    return results

def compute_friedman_test(algorithm_results_dict):
    """
    Computes Friedman test across matched experimental runs.
    algorithm_results_dict: dict mapping algorithm_name -> list of metric values across runs
    """
    alg_names = list(algorithm_results_dict.keys())
    data_arrays = [np.array(algorithm_results_dict[alg]) for alg in alg_names]
    
    # Verify equal lengths
    min_len = min(len(arr) for arr in data_arrays)
    trimmed_arrays = [arr[:min_len] for arr in data_arrays]
    
    # Compute Friedman Chi-square
    res = stats.friedmanchisquare(*trimmed_arrays)
    chi2_stat = float(res.statistic)
    p_val = float(res.pvalue)
    
    # Compute average ranks across blocks (higher value = better rank for maximization metrics like HV)
    matrix = np.column_stack(trimmed_arrays) # Shape (num_runs, num_algs)
    ranks = np.zeros_like(matrix)
    for row_idx in range(len(matrix)):
        # stats.rankdata assigns rank 1 to smallest; for maximization we invert so highest gets rank 1
        ranks[row_idx] = stats.rankdata(-matrix[row_idx])
        
    avg_ranks = np.mean(ranks, axis=0)
    ranking_dict = {alg: float(avg_ranks[i]) for i, alg in enumerate(alg_names)}
    
    return {
        "chi2_statistic": chi2_stat,
        "degrees_of_freedom": len(alg_names) - 1,
        "p_value": p_val,
        "average_ranks": ranking_dict,
        "significant": p_val < 0.05
    }

def compute_bootstrap_ci(x, y, num_bootstrap=2000, alpha=0.05, seed=42):
    """
    Computes 95% Bootstrap Confidence Intervals for paired difference (x - y) in mean and median.
    """
    rng = np.random.RandomState(seed)
    diffs = np.array(x, dtype=float) - np.array(y, dtype=float)
    n = len(diffs)
    
    boot_means = []
    boot_medians = []
    for _ in range(num_bootstrap):
        sample = rng.choice(diffs, size=n, replace=True)
        boot_means.append(np.mean(sample))
        boot_medians.append(np.median(sample))
        
    lower_pct = 100 * (alpha / 2.0)
    upper_pct = 100 * (1.0 - alpha / 2.0)
    
    mean_ci = (float(np.percentile(boot_means, lower_pct)), float(np.percentile(boot_means, upper_pct)))
    median_ci = (float(np.percentile(boot_medians, lower_pct)), float(np.percentile(boot_medians, upper_pct)))
    
    return {
        "mean_diff": float(np.mean(diffs)),
        "mean_ci_95": mean_ci,
        "median_diff": float(np.median(diffs)),
        "median_ci_95": median_ci
    }

def compute_nemenyi_critical_difference(num_algorithms, num_runs, alpha=0.05):
    """
    Computes Nemenyi post-hoc Critical Difference (CD) threshold for Friedman rank comparisons:
    CD = q_alpha * sqrt(k * (k + 1) / (6 * N))
    """
    # Studentized range q_alpha / sqrt(2) values for alpha = 0.05 (Demšar, 2006)
    q_alpha_table = {
        2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850,
        7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164, 11: 3.219, 12: 3.268
    }
    q_val = q_alpha_table.get(num_algorithms, 3.031)
    k = num_algorithms
    n = num_runs
    cd = q_val * np.sqrt((k * (k + 1.0)) / (6.0 * n))
    return float(cd)

