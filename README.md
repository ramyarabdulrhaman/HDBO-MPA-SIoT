# HDBO-MPA: Multi-Objective Service Discovery Toolkit for Social IoT

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Baselines: 11](https://img.shields.io/badge/algorithms-11%20implemented-green.svg)](#implemented-algorithms)

A high-performance Python framework for multi-objective service discovery and routing in the Social Internet of Things (SIoT). It provides implementations of the **Hybrid Dung Beetle Optimization and Marine Predators Algorithm (HDBO-MPA)** alongside 10 baseline algorithms, an attack-resilient composite trust engine, continuous-to-discrete graph decoders, and multi-criteria decision making (TOPSIS).

---

## 1. Implemented Algorithms

| Category | Algorithms |
| :--- | :--- |
| **Proposed Hybrid** | `HDBO-MPA` (Co-evolutionary dual-swarm with shared Pareto archive) |
| **Swarm Metaheuristics** | `DBO` (Dung Beetle Optimizer), `MPA` (Marine Predators Algorithm), `MOMPA`, `MO-PSO`, `MO-GWO`, `ACO` |
| **Evolutionary Multi-Objective** | `NSGA-II`, `MOEA/D`, `SPEA2` |
| **Classical Baselines** | `Dijkstra` (QoS Shortest Path), `T-Greedy` (Trust Greedy Forwarding) |

---

## 2. Practical Framework Architecture

- **Composite Trust Engine:** Integrates Laplace direct trust histories, Shannon entropy recommender weights, and a **Median Absolute Deviation (MAD)** consensus filter possessing a 50% statistical breakdown point against dishonest rating attacks (collusion rings, bad-mouthing, ballot-stuffing).
- **Social Graph Modeling:** Attributed directed graphs supporting Atzori's five canonical SIoT relationship ties (POR, CLOR, CWOR, SOR, OOR).
- **Topological Graph Decoders:** Continuous-to-discrete random-key priority vector decoder with chronological loop-erasure cycle purging and residual Dijkstra fallback, guaranteeing 100% loop-free valid paths on connected topologies.
- **Decision Terminal:** Integrated **TOPSIS** multi-criteria evaluation to automatically select the optimal compromise path $P^*$ from the non-dominated Pareto repository.

---

## 3. Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### Quick Install
```bash
git clone https://github.com/ramyarabdulrhaman/HDBO-MPA-SIoT.git
cd HDBO-MPA-SIoT
pip install -r requirements.txt
```

Or install in editable development mode:
```bash
pip install -e .
```

---

## 4. Practical Python Usage Example

```python
from src.network.siot_graph import SIoTGraphGenerator
from src.trust_model.engine import CompositeTrustEngine
from src.hybrid_optimizer.hdbo_mpa import HDBOMPAOptimizer

# 1. Load or generate a Social IoT graph topology (e.g., 100 nodes)
graph_gen = SIoTGraphGenerator(n_nodes=100, seed=42)
siot_network = graph_gen.generate_from_snap(subgraph_size=100)

# 2. Compute the pairwise composite trust matrix
trust_engine = CompositeTrustEngine(decay_factor=0.95)
trust_matrix = trust_engine.compute_matrix(siot_network)

# 3. Initialize HDBO-MPA optimizer
optimizer = HDBOMPAOptimizer(
    network=siot_network,
    trust_matrix=trust_matrix,
    pop_size=30,
    max_iter=50,
    archive_size=50
)

# 4. Execute multi-objective service discovery from source to target
source_node, target_node = 0, 85
pareto_front, best_path = optimizer.find_optimal_service_path(
    source=source_node,
    target=target_node,
    objectives=['trust', 'latency', 'energy', 'reliability']
)

print(f"Optimal Discovery Route: {best_path.nodes}")
print(f"Path QoS: Latency={best_path.latency:.2f}ms, Energy={best_path.energy:.2f}mJ, Trust={best_path.trust:.3f}")
```

---

## 5. Running Tests, Benchmarks & Visualizations

### 1. Run Sanity Smoke Test
Verify that the trust model, decoders, and all 11 optimization algorithms function correctly:
```bash
python tests/smoke_test.py
```

### 2. Run Master Benchmark Experiments
Execute 30 Monte Carlo runs across network sizes ($N = 100, 250, 500, 1000$):
```bash
python experiments/run_experiments.py
```

### 3. Compute Statistical Summaries
Calculate Hypervolume (HV), Generational Distance (GD), Spacing ($S$), Wilcoxon tests, and Friedman ranks:
```bash
python src/evaluation/process_results.py
```

### 4. Generate Performance Plots
Render high-resolution Pareto fronts, convergence curves, and boxplots:
```bash
python src/visualization/plotter.py
```

---

## 6. Directory Structure

```
HDBO-MPA-SIoT/
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Package build metadata
├── LICENSE                      # MIT Open Source License
├── README.md                    # Practical documentation
├── src/                         # Core Python library
│   ├── network/                 # SIoT graph generation & SNAP topology loader
│   ├── trust_model/             # Laplace-Shannon-MAD trust engine & attacks
│   ├── path_encoding/           # Priority vector decoder & loop-erasure
│   ├── dbo/                     # Dung Beetle Optimizer module
│   ├── mpa/                     # Marine Predators Algorithm module
│   ├── hybrid_optimizer/        # HDBO-MPA co-evolutionary optimizer
│   ├── baselines/               # NSGA-II, MOEA/D, SPEA2, MO-PSO, ACO, Dijkstra
│   ├── evaluation/              # Hypervolume, GD, IGD, Spacing, Wilcoxon, Friedman
│   └── visualization/           # Publication plotter scripts
├── experiments/                 # Benchmark execution runners & raw data
├── tests/                       # Test suite (smoke test and unit tests)
├── data/                        # Network datasets and SNAP topology definitions
├── graph_instances/             # Pre-generated JSON network benchmarks
├── figures/                     # Generated performance figures
└── tables/                      # Experimental result tables (CSV format)
```

---

## 7. Experimental Results Summary (SNAP-250)

| Algorithm | Mean Latency (ms) ↓ | Mean Energy (mJ) ↓ | Mean Path Trust ↑ | Mean Hops ↓ | Hypervolume (HV) ↑ | Generational Distance (GD) ↓ | Spacing (SP) ↓ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Dijkstra | 38.45 ± 4.12 | 2.85 ± 0.35 | 0.584 ± 0.052 | 3.4 ± 0.5 | 0.3842 ± 0.031 | 0.0891 ± 0.008 | 0.0762 ± 0.006 |
| T-Greedy | 152.34 ± 14.80 | 11.95 ± 1.25 | 0.932 ± 0.021 | 11.8 ± 1.4 | 0.4120 ± 0.028 | 0.0784 ± 0.007 | 0.0691 ± 0.005 |
| ACO | **32.18 ± 3.45** | **2.45 ± 0.28** | 0.612 ± 0.048 | **3.1 ± 0.4** | 0.5204 ± 0.024 | 0.0512 ± 0.005 | 0.0448 ± 0.004 |
| MO-PSO | 44.12 ± 4.80 | 3.42 ± 0.40 | 0.695 ± 0.042 | 4.2 ± 0.6 | 0.5312 ± 0.022 | 0.0465 ± 0.004 | 0.0410 ± 0.004 |
| NSGA-II | 68.45 ± 6.90 | 5.34 ± 0.58 | 0.762 ± 0.038 | 6.1 ± 0.8 | 0.5418 ± 0.020 | 0.0432 ± 0.004 | 0.0385 ± 0.003 |
| MOEA/D | 74.20 ± 7.50 | 5.82 ± 0.62 | 0.778 ± 0.035 | 6.5 ± 0.8 | 0.5491 ± 0.019 | 0.0398 ± 0.004 | 0.0361 ± 0.003 |
| SPEA2 | 62.15 ± 6.20 | 4.89 ± 0.52 | 0.751 ± 0.040 | 5.6 ± 0.7 | 0.5583 ± 0.018 | 0.0365 ± 0.003 | 0.0332 ± 0.003 |
| MOMPA | 58.90 ± 5.80 | 4.65 ± 0.48 | 0.784 ± 0.036 | 5.3 ± 0.7 | 0.5698 ± 0.017 | 0.0320 ± 0.003 | 0.0298 ± 0.003 |
| DBO | 147.12 ± 13.90 | 12.35 ± 1.18 | 0.915 ± 0.024 | 12.2 ± 1.5 | 0.5642 ± 0.018 | 0.0341 ± 0.003 | 0.0315 ± 0.003 |
| MPA | 149.82 ± 14.20 | 12.18 ± 1.15 | 0.921 ± 0.022 | 11.9 ± 1.4 | 0.5745 ± 0.016 | 0.0312 ± 0.003 | 0.0285 ± 0.003 |
| **HDBO-MPA** | **46.51 ± 4.95** | **3.67 ± 0.42** | **0.842 ± 0.031** | **4.6 ± 0.6** | **0.6842 ± 0.014** | **0.0142 ± 0.002** | **0.0165 ± 0.002** |

---

## 8. Authors & Maintainers

- **Ramyar A. Teimoor** (`ramyar.teimoor@univsul.edu.iq`)  
  *Department of Computer, College of Science, University of Sulaimani, Sulaimanyah, Kurdistan Region, Iraq*
- **Bahar Allakaram Tawfeeq** (`bahar.tawfeeq@univsul.edu.iq`)  
  *Department of Computer, College of Science, University of Sulaimani, Sulaimanyah, Kurdistan Region, Iraq*

---

## 9. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
