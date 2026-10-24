# Table VI: Systematic Component Ablation Study (Variants A0 Through A10, 30 Runs Each)

| Variant Code              | Description                     | Hypervolume (HV)    | Wilcoxon vs A0   |   Pareto Front Size |   Trust Score |   Latency (ms) |   Energy (mJ) |   QoS Index | Cycle/Loop Frequency (%)   |
|:--------------------------|:--------------------------------|:--------------------|:-----------------|--------------------:|--------------:|---------------:|--------------:|------------:|:---------------------------|
| **A0_Full_HDBO_MPA**      | Full Proposed Model             | **0.3097 ± 0.1310** | Baseline         |                29.9 |         0.575 |           40.9 |          2.72 |       0.787 | 0.0%                       |
| A1_DBO_Only               | DBO Sub-Population Only         | 0.2500 ± 0.1508     | p=0.0168         |                30.5 |         0.618 |          119.6 |          9.64 |       0.492 | 0.0%                       |
| A2_MPA_Only               | MPA Sub-Population Only         | 0.3473 ± 0.0961     | p=0.0207         |                29.7 |         0.607 |           91.4 |          6.55 |       0.498 | 0.0%                       |
| A3_No_Entropy_Weighting   | Uniform Recommender Weights     | 0.3081 ± 0.1128     | p=0.6959         |                31   |         0.557 |           39.4 |          2.46 |       0.823 | 0.0%                       |
| A4_Direct_Trust_Only      | Excludes Indirect/Social Trust  | 0.3474 ± 0.1533     | p=0.1386         |                34.2 |         0.687 |           43.2 |          3.01 |       0.777 | 0.0%                       |
| A5_No_Social_Relationship | Excludes Atzori Social Ties     | 0.2886 ± 0.1453     | p=0.9672         |                28   |         0.595 |           42.7 |          2.79 |       0.714 | 0.0%                       |
| A6_No_Indirect_Trust      | Excludes Recommender Feedback   | 0.3443 ± 0.1265     | p=0.0744         |                30.5 |         0.625 |           38.5 |          2.6  |       0.799 | 0.0%                       |
| A7_Sequential_Hybrid      | Sequential DBO to MPA           | 0.2435 ± 0.1608     | p=0.0011         |                28.8 |         0.59  |           49.4 |          3.45 |       0.671 | 0.0%                       |
| A8_Random_Selection       | Random-Key (No Heuristic Score) | 0.3803 ± 0.0559     | p=0.0053         |                14.1 |         0.544 |           34.4 |          2.02 |       0.908 | 0.0%                       |
| A9_No_Loop_Erasure        | Raw Traversal (No Loop-Erasure) | 0.3868 ± 0.0687     | p=0.0005         |                14.2 |         0.566 |           35.2 |          1.92 |       0.903 | 0.0%                       |
| A10_No_Archive_Crowding   | Random Archive Pruning          | 0.3238 ± 0.1207     | p=0.1597         |                27.9 |         0.573 |           39.6 |          2.57 |       0.81  | 0.0%                       |
