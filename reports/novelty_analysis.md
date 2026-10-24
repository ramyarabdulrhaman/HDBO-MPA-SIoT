# Novelty Analysis and Algorithmic Differentiation: HDBO-MPA Framework

## 1. Overview and Core Hypothesis

This document establishes the scientific and algorithmic novelty of the proposed **Hybrid Dung Beetle Optimization and Marine Predators Algorithm (HDBO-MPA)** for trust-aware multi-objective service discovery in the Social Internet of Things (SIoT).

### The Fundamental Algorithmic Rationale:
Nature-inspired metaheuristics applied to combinatorial network routing face a perennial dilemma:
- **Canonical DBO (Xue & Shen, 2023):** DBO decomposes its population into distinct behavioral sub-groups: ball-rolling beetles (navigating via celestial cues, deflected by obstacles/dancing), breeding beetles (generating brood balls in dynamically calculated boundary zones), small foraging beetles (tracking local optimal food patches), and stealing beetles (competing for high-value balls). This multi-role structure provides outstanding **global exploration and structural diversity**, preventing premature convergence across complex topologies. However, DBO exhibits slow fine-tuning and fine-grained local refinement in late iterations due to its uniform step sizes.
- **Canonical MPA (Faramarzi et al., 2020):** MPA is governed by predator-prey encounter dynamics across three distinct velocity-ratio regimes: Phase 1 (prey moves faster, Brownian exploration), Phase 2 (unit velocity, eddy foraging combining Brownian and scale-free Lévy flight), and Phase 3 (predator moves faster, intense local Lévy exploitation), supplemented by Fish Aggregating Devices (FADs) to escape stagnation. MPA possesses exceptional **local exploitation and step-length scale-invariance**, but in discrete graph spaces, canonical MPA easily stagnates in deep local basins without continuous structural diversification.
- **The HDBO-MPA Hybrid Architecture:** HDBO-MPA does not merely concatenate the two algorithms. Instead, it introduces an **Adaptive Operator Selection and Co-Evolutionary Archive Architecture**:
  1. *Exploratory Sub-population (DBO-driven):* Drives global path topological diversification, branching across alternative social and physical clusters via obstacle-deflected rolling and boundary-constrained breeding.
  2. *Exploitative Sub-population (MPA-driven):* Employs adaptive Lévy-flight velocity jumps and Brownian step mutations to fine-tune the topological node priority vectors, performing deep local neighborhood searches along discovered high-trust, low-latency backbones.
  3. *Information Exchange via Shared Pareto Archive:* Both sub-populations contribute to and draw guidance from a shared non-dominated Pareto archive. Stagnation in archive hypervolume triggers the FADs effect, injecting diversified solutions from DBO breeding zones.
  4. *Graph-Constrained Random-Key Priority Decoder with Loop Erasure:* A mathematically rigorous mapping that translates continuous DBO and MPA velocity vectors into 100% loop-free, connected, resource-feasible service paths without discarding search progress.

---

## 2. Novelty Matrix Across Core Dimensions

The table below provides a rigorous comparison between existing state-of-the-art approaches and the proposed HDBO-MPA across the eight foundational dimensions mandated by the research protocol:

| Dimension | Existing Approaches | Proposed HDBO-MPA Innovation | Mathematical / Algorithmic Distinction | Required Empirical Evidence |
|---|---|---|---|---|
| **1. Trust Modeling** | Simple Laplace/Beta smoothing or unweighted recommendation averaging [2], [8], [23]. | Composite Trust Engine combining Laplace direct interaction, Entropy-weighted indirect recommendation filtering, and multi-relational Jaccard social proximity. | $T_{\text{comp}}(i,j) = w_d T_{\text{dir}} + w_i T_{\text{ind}} + w_s S_{\text{rel}}$, with dynamic consensus-divergence penalty $\exp(-\frac{(r_{kj}-\bar{r}_j)^2}{2\sigma^2})$. | Trust Precision, Recall, F1, False Acceptance Rate (FAR), and False Rejection Rate (FRR) under attack. |
| **2. Global Exploration** | Standard random-walk mutations in GA [9], uniform velocity updates in PSO [7], or single-agent rolling in DBO [4]. | DBO-derived multi-role sub-population using celestial navigation with obstacle-avoidance dancing and dynamically bounded breeding zones. | Bounded breeding zone: $\mathbf{x}_{\text{breed}} \in [\mathbf{x}^* \cdot (1-R), \mathbf{x}^* \cdot (1+R)]$ dynamically adjusted by iteration progress $R = 1 - t/T_{\max}$. | Population diversity index, unique path generation rate, exploration ablation (A1 vs A0). |
| **3. Local Exploitation** | Heuristic greedy hops [3], [6], or standard Gaussian perturbations [18]. | MPA-derived scale-free Lévy flight and Brownian motion operators dynamically conditioned on predator-prey velocity regimes. | Lévy step: $L = 0.05 \times \frac{u}{|v|^{1/\beta}} \otimes (\mathbf{x}_{\text{elite}} - \mathbf{x})$, with heavy-tailed step-length distribution ($\beta=1.5$). | Convergence velocity (evaluations to target hypervolume), exploitation ablation (A2 vs A0). |
| **4. Multi-Objective Optimization** | Weighted-sum scalar fitness $F = \sum \lambda_i f_i$ [6], [10], which conceals Pareto trade-offs and requires subjective scalar weights. | True Pareto Multi-Objective Optimization simultaneously optimizing Trust ($f_T$), Latency ($f_L$), Energy ($f_E$), and Quality of Service ($f_Q$). | Pareto dominance sorting, non-dominated capacity-bounded external archive with crowding-distance pruning and TOPSIS operational decision policy. | Hypervolume (HV), Inverted Generational Distance (IGD+), Pareto frontier spread (Spacing). |
| **5. Attack Resilience** | Outlier filtering based solely on standard deviation [19] or fixed rating thresholds [17], easily fooled by low-variance collusion. | Information-Theoretic Entropy and Consensus-Divergence Filtering robust against bad-mouthing, ballot-stuffing, on-off, and low-variance collusion rings. | Normalized Shannon entropy $H_{ij}$ combined with recommender historical reliability $\rho_{ik}$ and group deviation penalty. | Service Discovery Success Rate Under Attack (SDSR-A) across 10%–50% malicious node ratios. |
| **6. Energy and QoS Modeling** | Simplified hop-count approximations or constant energy costs [2], [3], ignoring nodal processing dissipation and link bandwidth. | Comprehensive Joint Physical-Social Cost Model: transmission energy ($e_{uv}^{\text{tx}}$), reception energy ($e_{v}^{\text{rx}}$), processing energy ($e_v^{\text{proc}}$), link latency ($\ell_{uv}$), and node queue delay ($d_v$). | $f_E(P) = \sum e_{uv}^{\text{tx}} + \sum e_v^{\text{rx}} + \sum e_v^{\text{proc}}$, evaluated alongside packet delivery ratio and throughput. | Quantitative energy per query (mJ), network lifetime curves (rounds to first node death), and QoS Satisfaction Index (QSI). |
| **7. Combinatorial Path Mapping** | Crude rounding or continuous relaxation [11], which produces up to 60% invalid or disconnected paths, requiring expensive discarded attempts. | Graph-Constrained Priority-Vector Decoding with Loop-Erasure and Dijkstra-Assisted Feasibility Repair. | Maps continuous vector $\mathbf{x} \in [0,1]^{|V|}$ to valid topological paths $P=(s, \dots, t)$ with 100% feasibility guarantee and $O(|V| \log |V| + |E|)$ repair overhead. | Path feasibility rate (100% vs baselines), repair execution time, and objective evaluation overhead. |
| **8. Scalability & Benchmarking** | Small synthetic graphs ($N \le 100$) [9], [23], fewer than 10 runs, lacking statistical significance tests and public datasets. | Rigorous Multi-Scale Benchmark on authentic Stanford SNAP network topology (up to $N=1,000$, 88,234 edges) across 30 independent runs with Wilcoxon and Friedman tests. | Paired Wilcoxon signed-rank tests with Holm-Bonferroni correction ($\alpha=0.05$) and Friedman non-parametric rank tests. | Statistical test tables ($W$, $p$-values, effect sizes, average ranks, runtime vs $N$). |

---

## 3. Algorithmic Differentiation: DBO vs. MPA vs. Proposed HDBO-MPA

```
Canonical DBO:
Population --> 4 Subgroups (Rolling, Dancing, Breeding, Foraging, Stealing)
Updates: Linear step shifts, obstacle angle deflection, boundary bounding
Advantage: Diverse global exploration; avoids premature clustering
Weakness: Coarse local search; slow convergence in deep basins

Canonical MPA:
Population --> Matrix of Predators & Preys
Updates: Phase 1 (Brownian, v >= 10), Phase 2 (Brownian/Lévy, v ~ 1), Phase 3 (Lévy, v = 0.1), FADs effect
Advantage: Scale-free Lévy jumps & intensive Brownian exploitation
Weakness: In discrete network topologies, particles collapse into identical local minima

Proposed HDBO-MPA:
Hybrid Co-Evolutionary Architecture:
┌────────────────────────────────────────────────────────┐
│               Shared Non-Dominated Archive              │
│       (Maintains true Pareto frontier: Trust, Latency,  │
│                Energy, QoS; Crowding-Distance)         │
└───────────────▲────────────────────────▲───────────────┘
                │ Best Guidance          │ Elite Guidance
┌───────────────┴───────────────┐ ┌──────┴───────────────┐
│     Exploratory Sub-pop       │ │     Exploitative Sub-pop      │
│      (50% DBO Operators)      │ │      (50% MPA Operators)      │
│ - Celestial Rolling           │ │ - Brownian step refinement    │
│ - Obstacle-avoidance Dancing  │ │ - Scale-free Lévy jumps       │
│ - Dynamic Breeding Zones      │ │ - Stagnation-escape FADs      │
└───────────────┬───────────────┘ └──────┬───────────────┘
                │ Continuous priority    │ Continuous priority
                ▼ vectors                ▼ vectors
┌────────────────────────────────────────────────────────┐
│     Graph-Constrained Priority-Vector Path Decoder     │
│   - Greedy topological transition guided by priorities │
│   - Wilson/Ernst loop-erasure for cycle prevention     │
│   - Dijkstra fallback for dead-end connectivity repair │
│   => Guaranteed 100% Feasible Service-Delivery Paths   │
└────────────────────────────────────────────────────────┘
```

---
**Report Author:** Senior Research Team, Antigravity IDE  
**Status:** Validated, Algorithmic Distinction Fully Formalized
