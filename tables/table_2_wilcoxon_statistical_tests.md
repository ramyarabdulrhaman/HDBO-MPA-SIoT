# Table II: Pairwise Wilcoxon Signed-Rank Test with Holm-Bonferroni Correction & Bootstrap 95% CIs (Hypervolume)

| Comparison                |   W Stat |   Z-Score |   Raw $p$-value |   Adjusted $\alpha$ |   Rank-Biserial ($r$) | Mean Diff (95% CI)         | Statistically Significant?                   |
|:--------------------------|---------:|----------:|----------------:|--------------------:|----------------------:|:---------------------------|:---------------------------------------------|
| HDBO-MPA vs. **T-Greedy** |      0   |    -4.782 |      1.8626e-09 |              0.005  |                 0.873 | +0.2767 [0.2377, 0.3144]   | **Yes (HDBO-MPA > Baseline, p < alpha_adj)** |
| HDBO-MPA vs. **ACO**      |     53   |    -3.692 |      0.00023157 |              0.0056 |                 0.674 | -0.0742 [-0.1061, -0.0422] | **Yes (ACO > HDBO-MPA, p < alpha_adj)**      |
| HDBO-MPA vs. **MO-PSO**   |     56   |    -3.347 |      0.00084956 |              0.0063 |                 0.633 | -0.0630 [-0.1043, -0.0220] | **Yes (MO-PSO > HDBO-MPA, p < alpha_adj)**   |
| HDBO-MPA vs. **Dijkstra** |     74   |    -3.26  |      0.0011545  |              0.0071 |                 0.595 | +0.0837 [0.0387, 0.1225]   | **Yes (HDBO-MPA > Baseline, p < alpha_adj)** |
| HDBO-MPA vs. **DBO**      |     67.5 |    -3.243 |      0.001224   |              0.0083 |                 0.602 | +0.1016 [0.0561, 0.1498]   | **Yes (HDBO-MPA > Baseline, p < alpha_adj)** |
| HDBO-MPA vs. **MPA**      |     78.5 |    -2.655 |      0.0082213  |              0.01   |                 0.511 | -0.0465 [-0.0778, -0.0188] | **Yes (MPA > HDBO-MPA, p < alpha_adj)**      |
| HDBO-MPA vs. **NSGA-II**  |    132.5 |    -1.838 |      0.06766    |              0.0125 |                 0.341 | +0.0399 [0.0027, 0.0799]   | No (Indistinguishable)                       |
| HDBO-MPA vs. **MOEA/D**   |    137   |    -1.741 |      0.083656   |              0.0167 |                 0.323 | +0.0438 [-0.0050, 0.0919]  | No (Indistinguishable)                       |
| HDBO-MPA vs. **SPEA2**    |    171   |    -1.005 |      0.31988    |              0.025  |                 0.187 | -0.0053 [-0.0414, 0.0360]  | No (Indistinguishable)                       |
| HDBO-MPA vs. **MOMPA**    |    196   |    -0.465 |      0.64977    |              0.05   |                 0.086 | +0.0142 [-0.0306, 0.0618]  | No (Indistinguishable)                       |
