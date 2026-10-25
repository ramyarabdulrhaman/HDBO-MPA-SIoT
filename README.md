# HDBO-MPA: Trust-Aware Multi-Objective Service Discovery in Social IoT

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Algorithms: 11](https://img.shields.io/badge/Algorithms-11%20Baselines-green.svg)](#5-summary-of-experimental-results)

This repository contains the official, fully reproducible implementation, experimental benchmarks, and source code for:

> **A Hybrid Dung Beetle Optimization and Marine Predators Algorithm (HDBO-MPA) for Trust-Aware Multi-Objective Service Discovery in Social IoT**  
> *Authors:* Ramyar A. Teimoor and Bahar Allakaram Tawfeeq (Corresponding Author)  
> *Affiliation:* Department of Computer, College of Science, University of Sulaimani, Sulaimanyah, Kurdistan Region, Iraq  
> *Repository:* [https://github.com/ramyarabdulrhaman/HDBO-MPA-SIoT](https://github.com/ramyarabdulrhaman/HDBO-MPA-SIoT)

---

## 1. Research Overview

In the Social Internet of Things (SIoT), billions of autonomous smart devices establish social-like relationships (e.g., co-location, co-work, ownership) to discover and compose distributed services. However, decentralized service discovery faces two fundamental challenges:
1. **Malicious and Byzantine Behaviors:** Self-promoting, bad-mouthing, ballot-stuffing, and opportunistic collusion severely corrupt discovery paths.
2. **Conflicting Multi-Objective QoS Constraints:** Simultaneously optimizing composite trust, end-to-end latency, path hop count, and node energy consumption is an NP-hard combinatorial routing problem.

**HDBO-MPA** introduces a synergistic metaheuristic architecture that fuses the global exploration agility of the **Dung Beetle Optimizer (DBO)** with the fine-grained predatory exploitation of the **Marine Predators Algorithm (MPA)**, mediated by a shared Pareto external archive and a topological priority-vector decoder.

![System Architecture](figures/figure_1_architecture.png)

---

## 2. Key Contributions

### 1. Composite Mathematical Trust Engine
- **Direct Trust:** Time-decayed Laplace-smoothed Bayesian interaction assessment ($\lambda_{rec} = 0.95$).
- **Indirect Trust with Anomaly Filtering:** Shannon entropy-weighted recommendation aggregation coupled with a **Median / Median Absolute Deviation (MAD)** consensus filter possessing a theoretical 50% statistical breakdown point against arbitrary outlier contamination [Lai & Bayraktar, 2020], alongside empirically demonstrated resilience against bad-mouthing, ballot-stuffing, strategic on-off behavior, and coordinated low-variance collusive syndicates.
- **Social Relationship Proximity:** Multi-relational Jaccard neighborhood similarity across Atzori's five canonical SIoT relationship types (POR, CWOR, CLOR, SOR, OOR).

### 2. HDBO-MPA Hybrid Metaheuristic Architecture
- **Exploratory DBO Sub-population:** Ball-rolling with celestial navigation, obstacle dancing, and dynamic boundary breeding zones.
- **Exploitative MPA Sub-population:** Scale-free Lévy flights and Brownian motion regimes conditioned on predator-prey velocity ratios.
- **Shared Non-Dominated External Archive:** Dynamic elite guidance and diversity-triggered Fish Aggregating Devices (FADs) perturbations.
- **Priority-Vector Decoder:** Continuous-to-discrete random-key priority vector decoder with loop-erasure cycle purging and residual Dijkstra fallback on physical links, guaranteeing conditional 100% loop-free topological feasibility across connected topologies.
- **Multi-Criteria Decision Making (TOPSIS):** Identifies the single best operational compromise path P* from the non-dominated Pareto front according to application weights.

### 3. Rigorous Empirical Benchmarking
- Evaluated on connected BFS snowball-sampled subgraphs of the Stanford SNAP ego-Facebook network ($N = 100, 250, 500, 1000$ nodes).
- 30 independent runs with strictly equalized 780-evaluation budgets across 11 benchmark algorithms (Dijkstra, T-Greedy, NSGA-II, MOEA/D, MO-PSO, ACO, MOMPA, SPEA2, DBO, MPA, HDBO-MPA).
- Non-parametric statistical validation: Paired directional Wilcoxon signed-rank tests with Holm-Bonferroni correction ($p < 0.05$) and Friedman non-parametric rank tests ($\chi_F^2 = 189.41$, Nemenyi $CD = 2.76$).
- Demonstrates ~3.2x latency and ~3.4x energy reduction relative to DBO (46.51 ms vs. 147.12 ms; 3.67 mJ vs. 12.35 mJ) and ~3.2x latency and ~3.3x energy reduction relative to MPA (46.51 ms vs. 149.82 ms; 3.67 mJ vs. 12.18 mJ) on SNAP-250, with 98.4% clinical SLA satisfaction in an emergency healthcare discovery scenario.

---

## 3. Repository Architecture

```
HDBO-MPA-SIoT/
├── requirements.txt             # Python environment dependencies
├── pyproject.toml               # Package build metadata
├── LICENSE                      # MIT Open Source License
├── README.md                    # Master documentation
├── src/                         # Core algorithmic implementations
│   ├── network/                 # SIoT network generation & graph topology
│   ├── trust_model/             # Composite trust engine & attack simulator
│   ├── path_encoding/           # Priority vector decoder & loop-erasure
│   ├── dbo/                     # Canonical Dung Beetle Optimizer
│   ├── mpa/                     # Canonical Marine Predators Algorithm
│   ├── hybrid_optimizer/        # Proposed HDBO-MPA hybrid optimizer
│   ├── baselines/               # NSGA-II, MO-PSO, ACO, MO-GWO, MOMA, Dijkstra
│   ├── evaluation/              # Hypervolume, Spread, Spacing, Wilcoxon, Friedman
│   └── visualization/           # Publication plotter (Figures 1-17)
├── experiments/                 # Benchmark runners & raw output data
│   ├── run_experiments.py       # Master benchmark orchestrator
│   ├── run_comprehensive_stats.py
│   ├── compute_stats.py
│   ├── benchmark_config.json    # Parameter specifications
│   └── raw_results/             # Full CSV benchmark results (30 independent runs)
├── tests/                       # Unit and integration test suite
│   └── smoke_test.py            # End-to-end sanity & verification test
├── data/                        # Datasets and graph definitions
│   ├── raw/                     # Stanford SNAP topology dataset
│   ├── checksums/               # SHA-256 integrity hashes
│   └── documentation/           # Data dictionary and provenance
├── graph_instances/             # Pre-generated SIoT graph benchmarks (JSON)
├── figures/                     # Publication figures (High-resolution 300 DPI)
├── tables/                      # Benchmark summary tables (CSV & Markdown)
└── scripts/                     # Figure generation and visualization scripts
```

---

## 4. Quick Start & Reproduction

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/ramyarabdulrhaman/HDBO-MPA-SIoT.git
cd HDBO-MPA-SIoT
pip install -r requirements.txt
```

Or install in editable mode:
```bash
pip install -e .
```

### 1. Run Quick Smoke Test
Verify the installation, trust engine, decoders, and all optimization modules:
```bash
python tests/smoke_test.py
```

### 2. Run Full Experimental Benchmark Suite
Execute the multi-objective benchmark suite across all 11 algorithms:
```bash
python experiments/run_experiments.py
```

### 3. Compute Statistical Summaries & Tables
Calculate Wilcoxon signed-rank tests, Holm-Bonferroni corrections, and Friedman rankings:
```bash
python src/evaluation/process_results.py
```

### 4. Regenerate All Publication Figures
Generate Figures 1 through 17 in high-resolution format:
```bash
python src/visualization/plotter.py
```

---

## 5. Summary of Experimental Results (SNAP-250 Benchmark)

| Algorithm | Mean Latency (ms) ↓ | Mean Energy (mJ) ↓ | Mean Path Trust ↑ | Mean Hops ↓ | Hypervolume (HV) ↑ | Generational Distance (GD) ↓ | Spacing (SP) ↓ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Dijkstra (QoS-only) | 38.45 ± 4.12 | 2.85 ± 0.35 | 0.584 ± 0.052 | 3.4 ± 0.5 | 0.3842 ± 0.031 | 0.0891 ± 0.008 | 0.0762 ± 0.006 |
| T-Greedy (Trust-only) | 152.34 ± 14.80 | 11.95 ± 1.25 | 0.932 ± 0.021 | 11.8 ± 1.4 | 0.4120 ± 0.028 | 0.0784 ± 0.007 | 0.0691 ± 0.005 |
| ACO | **32.18 ± 3.45** | **2.45 ± 0.28** | 0.612 ± 0.048 | **3.1 ± 0.4** | 0.5204 ± 0.024 | 0.0512 ± 0.005 | 0.0448 ± 0.004 |
| MO-PSO | 44.12 ± 4.80 | 3.42 ± 0.40 | 0.695 ± 0.042 | 4.2 ± 0.6 | 0.5312 ± 0.022 | 0.0465 ± 0.004 | 0.0410 ± 0.004 |
| NSGA-II | 68.45 ± 6.90 | 5.34 ± 0.58 | 0.762 ± 0.038 | 6.1 ± 0.8 | 0.5418 ± 0.020 | 0.0432 ± 0.004 | 0.0385 ± 0.003 |
| MOEA/D | 74.20 ± 7.50 | 5.82 ± 0.62 | 0.778 ± 0.035 | 6.5 ± 0.8 | 0.5491 ± 0.019 | 0.0398 ± 0.004 | 0.0361 ± 0.003 |
| SPEA2 | 62.15 ± 6.20 | 4.89 ± 0.52 | 0.751 ± 0.040 | 5.6 ± 0.7 | 0.5583 ± 0.018 | 0.0365 ± 0.003 | 0.0332 ± 0.003 |
| MOMPA | 58.90 ± 5.80 | 4.65 ± 0.48 | 0.784 ± 0.036 | 5.3 ± 0.7 | 0.5698 ± 0.017 | 0.0320 ± 0.003 | 0.0298 ± 0.003 |
| DBO | 147.12 ± 13.90 | 12.35 ± 1.18 | 0.915 ± 0.024 | 12.2 ± 1.5 | 0.5642 ± 0.018 | 0.0341 ± 0.003 | 0.0315 ± 0.003 |
| MPA | 149.82 ± 14.20 | 12.18 ± 1.15 | 0.921 ± 0.022 | 11.9 ± 1.4 | 0.5745 ± 0.016 | 0.0312 ± 0.003 | 0.0285 ± 0.003 |
| **HDBO-MPA (Proposed)** | **46.51 ± 4.95** | **3.67 ± 0.42** | **0.842 ± 0.031** | **4.6 ± 0.6** | **0.6842 ± 0.014** | **0.0142 ± 0.002** | **0.0165 ± 0.002** |

*All results reflect 30 independent runs under an equalized 780-evaluation budget. Pairwise Wilcoxon tests confirm statistically significant superiority over 8 of 10 baselines under Holm-Bonferroni correction (p < 0.05).*

---

## 6. Citation

If you find this research, algorithm, or codebase useful in your work, please cite:

```bibtex
@article{teimoor2026hdbo_mpa,
  title={A Hybrid Dung Beetle Optimization and Marine Predators Algorithm (HDBO-MPA) for Trust-Aware Multi-Objective Service Discovery in Social IoT},
  author={Teimoor, Ramyar A. and Tawfeeq, Bahar Allakaram},
  journal={IEEE Internet of Things Journal},
  year={2026},
  url={https://github.com/ramyarabdulrhaman/HDBO-MPA-SIoT}
}
```

---

## 7. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
