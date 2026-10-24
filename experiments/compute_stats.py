import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('experiments/raw_results/multi_objective_benchmark_raw.csv')

algs = ['HDBO-MPA', 'MPA', 'DBO', 'NSGA-II', 'MO-PSO', 'ACO', 'T-Greedy', 'Dijkstra']
hv_by_alg = {}
for alg in algs:
    hv_by_alg[alg] = df[df['algorithm'] == alg]['hypervolume'].values

print('--- Hypervolume Means and Stds (30 runs, N=250) ---')
for alg in algs:
    print(f'{alg:10s}: Mean={np.mean(hv_by_alg[alg]):.4f}, Std={np.std(hv_by_alg[alg]):.4f}')

hdbo_hv = hv_by_alg['HDBO-MPA']

print('\n--- Pairwise Wilcoxon Signed-Rank Test vs HDBO-MPA (Hypervolume) ---')
baselines = ['MPA', 'DBO', 'NSGA-II', 'MO-PSO', 'ACO', 'T-Greedy', 'Dijkstra']
results = []
for b in baselines:
    b_hv = hv_by_alg[b]
    diff = hdbo_hv - b_hv
    nonzero = diff[diff != 0]
    n = len(nonzero)
    res = stats.wilcoxon(hdbo_hv, b_hv, zero_method='wilcox', correction=True)
    w_stat = float(res.statistic)
    p_val = float(res.pvalue)
    mean_w = n * (n + 1) / 4.0
    var_w = n * (n + 1) * (2 * n + 1) / 24.0
    z_score = (w_stat - mean_w) / np.sqrt(var_w) if var_w > 0 else 0.0
    r = abs(z_score) / np.sqrt(n) if n > 0 else 0.0
    results.append({'baseline': b, 'W': w_stat, 'Z': z_score, 'p': p_val, 'r': r, 'n': n})

# Sort by raw p-value for Holm-Bonferroni
sorted_res = sorted(results, key=lambda x: x['p'])
m = len(sorted_res)
for k, row in enumerate(sorted_res, 1):
    alpha_adj = 0.05 / (m - k + 1)
    sig = row['p'] < alpha_adj
    print(f"vs {row['baseline']:10s} | W={row['W']:6.1f} | Z={row['Z']:7.3f} | p={row['p']:.6e} | alpha_adj={alpha_adj:.4f} | r={row['r']:.3f} | Sig={sig}")

# Friedman Test
fried_data = [hv_by_alg[a] for a in algs]
f_stat, f_p = stats.friedmanchisquare(*fried_data)
print(f'\nFriedman Test: Chi2={f_stat:.4f}, df={len(algs)-1}, p={f_p:.6e}')

# Average ranks
matrix = np.column_stack(fried_data)
ranks = np.zeros_like(matrix)
for i in range(len(matrix)):
    ranks[i] = stats.rankdata(-matrix[i]) # higher HV is better -> rank 1
avg_ranks = np.mean(ranks, axis=0)
print('\nFriedman Average Ranks (1=best):')
for a, rk in zip(algs, avg_ranks):
    print(f'{a:10s}: Avg Rank = {rk:.3f}')
