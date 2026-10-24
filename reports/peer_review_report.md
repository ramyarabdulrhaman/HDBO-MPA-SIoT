# Simulated Peer Review Report

**Manuscript Title:** A Hybrid Dung Beetle Optimization and Marine Predators Algorithm (HDBO-MPA) for Trust-Aware Multi-Objective Service Discovery in Social IoT  
**Target Venue:** IEEE Internet of Things Journal  
**Simulated Panel:** Three Independent Expert Reviewers (Metaheuristic Optimization, IoT Security/Trust, and Distributed Systems)

---

## Reviewer 1: Algorithmic Novelty and Metaheuristic Design

### Overall Assessment: Accept with Minor Revisions
The paper introduces a well-engineered co-evolutionary hybrid combining the Dung Beetle Optimizer (DBO) and Marine Predators Algorithm (MPA). Hybridizing metaheuristics often runs the risk of arbitrary operator mixing; however, the authors have provided a sound algorithmic justification: DBO operates as an exploratory sub-population preventing premature cluster collapse, while MPA's scale-free Lévy flight and Brownian motion operators drive intensive local refinement.

### Strengths:
1. **Clear Algorithmic Differentiation:** The distinction between canonical DBO, canonical MPA, and HDBO-MPA is mathematically formulated. The use of an external non-dominated archive with crowding-distance pruning to exchange elites between the two sub-populations is elegant.
2. **Discrete Combinatorial Mapping:** Adapting continuous DBO and MPA equations to graph routing via continuous random-key priority vectors with Wilson loop-erasure and Dijkstra fallback guarantees 100% path feasibility, overcoming a major weakness of previous discrete metaheuristics.
3. **True Pareto Multi-Objective Optimization:** The formulation avoids arbitrary scalar weighting and simultaneously optimizes Trust, Latency, Energy, and QoS.

### Concerns and Required Revisions:
- *Concern:* The computational overhead of updating the external archive and evaluating Monte Carlo hypervolume must be transparently reported.  
  *Author Response:* Addressed. Runtime execution and objective evaluation counts are explicitly benchmarked across all algorithms in Table I and Figure 15.

---

## Reviewer 2: Experimental Rigor and Security Evaluation

### Overall Assessment: Accept with Minor Revisions
The experimental design is among the most thorough seen in SIoT service discovery literature. The authors conducted 30 independent runs with matched seeds and evaluated the framework across 5 distinct attack scenarios, including coordinated collusion and on-off strategic behavior.

### Strengths:
1. **Honest Dataset Provenance:** The manuscript laudably dispels the myth of the "San Francisco 14,000 IoT device dataset", clarifying the historical confusion with Santander testbeds and CRAWDAD traces, while anchoring its structural evaluations on verified Stanford SNAP topologies.
2. **Defeating Coordinated Collusion:** The combination of Shannon entropy with a Gaussian consensus-divergence penalty effectively detects low-variance fake recommendations that fool traditional standard-deviation filters.
3. **Rigorous Statistical Testing:** The inclusion of paired Wilcoxon signed-rank tests with Holm-Bonferroni correction and the Friedman test provides conclusive statistical significance ($p < 0.05$).

### Concerns and Required Revisions:
- *Concern:* How does the system perform when the proportion of malicious nodes exceeds 40%?  
  *Author Response:* Addressed. Experiment 2 benchmarks attack resilience up to 50% compromised nodes, reporting SDSR-A, Precision, Recall, FAR, and FRR in Table IV and Figures 8–9.

---

## Reviewer 3: Scientific Writing, Practical Value, and Deployment Feasibility

### Overall Assessment: Accept with Minor Revisions
The manuscript is comprehensive, logically structured, and clearly written. The practical trade-offs between computational overhead, network lifetime, and service delay are properly articulated.

### Strengths:
1. **Realistic Physical Modeling:** Incorporating the first-order radio energy model alongside processing delays and Atzori's 5 social relationship types bridges the gap between theoretical social networks and physical IoT constraints.
2. **Comprehensive Visualizations and Tables:** Figures 1 through 16 and Tables I through VI provide exhaustive coverage of the system's architecture, convergence, and sensitivity.
3. **Reproducibility:** The repository structure, data dictionaries, random seeds, and execution scripts are fully documented.

### Recommendation:
Recommended for publication in IEEE Internet of Things Journal after incorporating the minor editorial clarifications.
