# Reproducibility Protocol and Execution Guide

This document provides complete, transparent instructions to independently reproduce all experiments, data synthesis pipelines, statistical tests, and publication figures for the **HDBO-MPA Social IoT Research Project**.

---

## 1. System Requirements and Environment

- **Operating System:** Windows 10/11 (or Linux/macOS with equivalent Python 3.10+ environment)
- **Python Version:** Python 3.12.10
- **Hardware Architecture:** Multi-core x86_64 CPU (minimum 4 cores, 16 GB RAM recommended)
- **Core Dependencies:**
  - `numpy >= 1.24.0`
  - `scipy >= 1.10.0`
  - `networkx >= 3.0`
  - `matplotlib >= 3.7.0`
  - `python-docx >= 1.0.0`

### 1.1 Dependency Installation
```bash
pip install numpy scipy networkx matplotlib python-docx
```
A complete `requirements.txt` file is located in the root repository directory.

---

## 2. Directory Structure Overview
```
HDBO_MPA_SIoT_Research/
├── data/
│   ├── raw/
│   │   ├── facebook_combined.txt
│   │   └── facebook_combined.txt.gz
│   ├── checksums/
│   │   └── sha256_checksums.txt
│   └── documentation/
│       └── data_dictionary.md
├── src/
│   ├── network/siot_graph.py
│   ├── trust_model/engine.py
│   ├── trust_model/attack_simulator.py
│   ├── path_encoding/representation.py
│   ├── dbo/dbo_optimizer.py
│   ├── mpa/mpa_optimizer.py
│   ├── hybrid_optimizer/hdbo_mpa.py
│   ├── baselines/baseline_models.py
│   ├── evaluation/metrics.py
│   ├── evaluation/statistical_tests.py
│   ├── evaluation/process_results.py
│   └── visualization/plotter.py
├── experiments/
│   ├── run_experiments.py
│   └── raw_results/
├── figures/
├── tables/
├── reports/
└── manuscript/
    ├── HDBO_MPA_SIoT_Article.docx
    ├── HDBO_MPA_SIoT_Article.tex
    └── references.bib
```

---

## 3. Step-by-Step Reproduction Instructions

### Step 1: Execute End-to-End Smoke Test
To verify that all classes, random-key decoders, trust engines, and baseline optimizers execute without errors:
```bash
python tests/smoke_test.py
```
*Expected Output:* Confirms successful loading of SNAP graph, trust matrix generation, 100% loop-free path decoding, and optimizer convergence.

### Step 2: Execute Master Benchmark Suite
To run all 5 experiments (Multi-Objective Benchmark across 30 runs, Attack Resilience, Scalability, Ablations, Sensitivity):
```bash
python experiments/run_experiments.py
```
*Output Artifacts:*
- `experiments/raw_results/multi_objective_benchmark_raw.csv`
- `experiments/raw_results/attack_resilience_raw.csv`
- `experiments/raw_results/scalability_raw.csv`
- `experiments/raw_results/ablation_study_raw.csv`
- `experiments/raw_results/sensitivity_analysis_raw.csv`

### Step 3: Process Statistical Tests and Generate Tables
To calculate descriptive statistics (Mean, Std, Median, IQR), Wilcoxon signed-rank tests with Holm-Bonferroni corrections, and Friedman rankings:
```bash
python src/evaluation/process_results.py
```
*Output Artifacts:*
- `tables/table_1_multiobjective_summary.md` and `.csv`
- `tables/table_2_wilcoxon_statistical_tests.md`
- `tables/table_3_friedman_ranks.md`
- `tables/table_4_attack_resilience.md`
- `tables/table_5_scalability.md`
- `tables/table_6_ablation_study.md`

### Step 4: Generate Publication Figures (Figures 1 through 16)
To generate all 16 high-resolution (300 DPI) scientific figures:
```bash
python src/visualization/plotter.py
```
*Output Artifacts:*
- `figures/figure_1_architecture.png` through `figures/figure_16_scalability.png`

---

## 4. Deterministic Random Seeds and Traceability

To ensure 100% deterministic reproducibility across runs:
- **Experiment 1 (Multi-Objective Benchmark):** Seeds `100, 101, ..., 129` (30 matched independent seeds).
- **Experiment 2 (Attack Resilience):** Seeds derived as `int(malicious_ratio * 100)`: `10, 20, 30, 40, 50`.
- **Experiment 3 (Scalability):** Seed `42`.
- **Experiment 4 (Ablation):** Seed `42`.
- **Experiment 5 (Sensitivity):** Seed `42`.
