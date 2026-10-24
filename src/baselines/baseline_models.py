"""
Baseline Optimization Algorithms for Social IoT Service Discovery.
Implements Dijkstra Shortest Path, Trust-Aware Greedy (T-Greedy),
Discrete MO-GA (NSGA-II), Discrete MO-PSO, and Discrete ACO.
"""

import math
import random
import heapq
import numpy as np
import networkx as nx
from src.evaluation.metrics import dominates, extract_pareto_front, topsis_selection

# -------------------------------------------------------------
# 1. Dijkstra Shortest Path Baseline
# -------------------------------------------------------------
class DijkstraBaseline:
    def __init__(self, encoder_decoder):
        self.encoder_decoder = encoder_decoder
        self.graph = encoder_decoder.graph

    def optimize(self, source, destination, weight='latency'):
        try:
            path = nx.shortest_path(self.graph, source=source, target=destination, weight=weight)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            path = [source, destination]
            
        objs = self.encoder_decoder.evaluate_objectives(path)
        solution = {"position": None, "path": path, "objectives": objs}
        return {
            "pareto_front": [solution],
            "best_compromise": solution,
            "eval_count": 1
        }

# -------------------------------------------------------------
# 2. Trust-Aware Greedy (T-Greedy) Baseline
# -------------------------------------------------------------
class TGreedyBaseline:
    def __init__(self, encoder_decoder, alpha_trust=0.70):
        self.encoder_decoder = encoder_decoder
        self.graph = encoder_decoder.graph
        self.composite_trust = encoder_decoder.composite_trust
        self.edge_attributes = encoder_decoder.edge_attributes
        self.alpha_trust = alpha_trust

    def optimize(self, source, destination, max_hops=15):
        path = [source]
        curr = source
        visited = {source}
        
        for _ in range(max_hops):
            if curr == destination:
                break
            neighbors = [n for n in self.graph.neighbors(curr) if n not in visited]
            if not neighbors:
                break
            if destination in neighbors:
                path.append(destination)
                break
                
            # Score neighbors by alpha_trust * trust + (1 - alpha_trust) * (1 / (latency + 1))
            best_nbr = None
            best_score = -1e9
            for nbr in neighbors:
                t = self.composite_trust.get((curr, nbr), 0.5)
                lat = self.edge_attributes.get((curr, nbr), {}).get("latency", 10.0)
                score = self.alpha_trust * t + (1.0 - self.alpha_trust) * (10.0 / (lat + 1.0))
                if score > best_score:
                    best_score = score
                    best_nbr = nbr
                    
            if best_nbr is None:
                break
            visited.add(best_nbr)
            path.append(best_nbr)
            curr = best_nbr
            
        if path[-1] != destination:
            try:
                repair = nx.shortest_path(self.graph, source=path[-1], target=destination, weight='latency')
                path.extend(repair[1:])
            except Exception:
                path = nx.shortest_path(self.graph, source=source, target=destination, weight='latency')
                
        objs = self.encoder_decoder.evaluate_objectives(path)
        solution = {"position": None, "path": path, "objectives": objs}
        return {
            "pareto_front": [solution],
            "best_compromise": solution,
            "eval_count": len(path)
        }

# -------------------------------------------------------------
# 3. Discrete Multi-Objective Genetic Algorithm (NSGA-II)
# -------------------------------------------------------------
class NSGAIIBaseline:
    def __init__(self, encoder_decoder, pop_size=40, max_iter=50, archive_capacity=50, 
                 crossover_rate=0.85, mutation_rate=0.15, seed=42):
        self.encoder_decoder = encoder_decoder
        self.num_nodes = encoder_decoder.num_nodes
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.archive_capacity = archive_capacity
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.archive = []

    def optimize(self, source, destination):
        # Population of priority vectors
        P = np.random.uniform(0.0, 1.0, size=(self.pop_size, self.num_nodes))
        
        # Initial evaluation
        pop = []
        for i in range(self.pop_size):
            path = self.encoder_decoder.decode(P[i], source, destination)
            objs = self.encoder_decoder.evaluate_objectives(path)
            pop.append({"position": P[i], "path": path, "objectives": objs})
            
        self.archive = extract_pareto_front(pop)
        eval_count = self.pop_size
        
        for t in range(self.max_iter):
            offspring = []
            while len(offspring) < self.pop_size:
                # Tournament selection
                p1, p2 = random.choice(pop), random.choice(pop)
                parent1 = p1["position"] if dominates(p1["objectives"], p2["objectives"]) else p2["position"]
                p3, p4 = random.choice(pop), random.choice(pop)
                parent2 = p3["position"] if dominates(p3["objectives"], p4["objectives"]) else p4["position"]
                
                # Crossover (simulated binary / uniform blend)
                child = parent1.copy()
                if random.random() < self.crossover_rate:
                    mask = np.random.uniform(0, 1, size=self.num_nodes) < 0.5
                    child[mask] = parent2[mask]
                    
                # Mutation (Gaussian noise)
                if random.random() < self.mutation_rate:
                    noise = np.random.normal(0, 0.1, size=self.num_nodes)
                    child = np.clip(child + noise, 0.0, 1.0)
                    
                path = self.encoder_decoder.decode(child, source, destination)
                objs = self.encoder_decoder.evaluate_objectives(path)
                offspring.append({"position": child, "path": path, "objectives": objs})
                eval_count += 1
                
            # Combine parent + offspring (2N)
            combined = pop + offspring
            # Extract non-dominated front
            self.archive = extract_pareto_front(self.archive + combined)
            if len(self.archive) > self.archive_capacity:
                self.archive = random.sample(self.archive, self.archive_capacity)
                
            # Select next generation N survivors
            pop = random.sample(combined, self.pop_size)
            
        return {
            "pareto_front": self.archive,
            "best_compromise": topsis_selection(self.archive),
            "eval_count": eval_count
        }

# -------------------------------------------------------------
# 4. Discrete Multi-Objective Particle Swarm Optimization (MO-PSO)
# -------------------------------------------------------------
class MOPSOBaseline:
    def __init__(self, encoder_decoder, pop_size=40, max_iter=50, archive_capacity=50,
                 w=0.6, c1=1.5, c2=1.5, seed=42):
        self.encoder_decoder = encoder_decoder
        self.num_nodes = encoder_decoder.num_nodes
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.archive_capacity = archive_capacity
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.archive = []

    def optimize(self, source, destination):
        # Position and Velocity
        X = np.random.uniform(0.0, 1.0, size=(self.pop_size, self.num_nodes))
        V = np.random.uniform(-0.1, 0.1, size=(self.pop_size, self.num_nodes))
        Pbest = X.copy()
        
        particles = []
        for i in range(self.pop_size):
            path = self.encoder_decoder.decode(X[i], source, destination)
            objs = self.encoder_decoder.evaluate_objectives(path)
            particles.append({"position": X[i], "path": path, "objectives": objs})
            
        self.archive = extract_pareto_front(particles)
        eval_count = self.pop_size
        
        for t in range(self.max_iter):
            for i in range(self.pop_size):
                # Pick leader gbest from archive
                leader = random.choice(self.archive)["position"] if self.archive else Pbest[i]
                r1, r2 = np.random.uniform(0, 1, size=self.num_nodes), np.random.uniform(0, 1, size=self.num_nodes)
                
                # Update velocity and position
                V[i] = self.w * V[i] + self.c1 * r1 * (Pbest[i] - X[i]) + self.c2 * r2 * (leader - X[i])
                V[i] = np.clip(V[i], -0.2, 0.2)
                X[i] = np.clip(X[i] + V[i], 0.0, 1.0)
                
                path = self.encoder_decoder.decode(X[i], source, destination)
                objs = self.encoder_decoder.evaluate_objectives(path)
                eval_count += 1
                
                sol = {"position": X[i].copy(), "path": path, "objectives": objs}
                particles[i] = sol
                
                # Update personal best if new solution dominates previous Pbest
                p_old_objs = self.encoder_decoder.evaluate_objectives(
                    self.encoder_decoder.decode(Pbest[i], source, destination)
                )
                if dominates(objs, p_old_objs):
                    Pbest[i] = X[i].copy()
                    
            self.archive = extract_pareto_front(self.archive + particles)
            if len(self.archive) > self.archive_capacity:
                self.archive = random.sample(self.archive, self.archive_capacity)
                
        return {
            "pareto_front": self.archive,
            "best_compromise": topsis_selection(self.archive),
            "eval_count": eval_count
        }

# -------------------------------------------------------------
# 5. Discrete Ant Colony Optimization (ACO)
# -------------------------------------------------------------
class ACOBaseline:
    def __init__(self, encoder_decoder, num_ants=20, max_iter=30, alpha=1.0, beta=2.0, rho=0.1, seed=42):
        self.encoder_decoder = encoder_decoder
        self.graph = encoder_decoder.graph
        self.num_nodes = encoder_decoder.num_nodes
        self.num_ants = num_ants
        self.max_iter = max_iter
        self.alpha = alpha # Pheromone influence
        self.beta = beta   # Heuristic visibility influence
        self.rho = rho     # Pheromone evaporation rate
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.archive = []
        
        # Initialize pheromone table on edges
        self.pheromones = {}
        for u, v in self.graph.edges():
            self.pheromones[(u, v)] = 1.0
            self.pheromones[(v, u)] = 1.0

    def optimize(self, source, destination, max_hops=15):
        eval_count = 0
        all_solutions = []
        
        for t in range(self.max_iter):
            iter_solutions = []
            for ant in range(self.num_ants):
                path = [source]
                visited = {source}
                curr = source
                
                for _ in range(max_hops):
                    if curr == destination:
                        break
                    neighbors = [n for n in self.graph.neighbors(curr) if n not in visited]
                    if not neighbors:
                        break
                    if destination in neighbors:
                        path.append(destination)
                        break
                        
                    # Transition probabilities: p_ij = (tau_ij^alpha) * (eta_ij^beta) / sum(...)
                    probs = []
                    for nbr in neighbors:
                        tau = self.pheromones.get((curr, nbr), 1.0) ** self.alpha
                        # Visibility eta: trust / latency
                        t_val = self.encoder_decoder.composite_trust.get((curr, nbr), 0.5)
                        lat = self.encoder_decoder.edge_attributes.get((curr, nbr), {}).get("latency", 10.0)
                        eta = (t_val / (lat + 1.0)) ** self.beta
                        probs.append(tau * eta)
                        
                    sum_p = sum(probs)
                    if sum_p > 1e-9:
                        probs = [p / sum_p for p in probs]
                        chosen_nbr = np.random.choice(neighbors, p=probs)
                    else:
                        chosen_nbr = random.choice(neighbors)
                        
                    visited.add(chosen_nbr)
                    path.append(chosen_nbr)
                    curr = chosen_nbr
                    
                # Repair if incomplete
                if path[-1] != destination:
                    try:
                        repair = nx.shortest_path(self.graph, source=path[-1], target=destination, weight='latency')
                        path.extend(repair[1:])
                    except Exception:
                        path = nx.shortest_path(self.graph, source=source, target=destination, weight='latency')
                        
                objs = self.encoder_decoder.evaluate_objectives(path)
                eval_count += 1
                sol = {"position": None, "path": path, "objectives": objs}
                iter_solutions.append(sol)
                
            # Evaporation
            for edge in self.pheromones:
                self.pheromones[edge] *= (1.0 - self.rho)
                
            # Reinforcement for non-dominated paths
            iter_pareto = extract_pareto_front(iter_solutions)
            for sol in iter_pareto:
                p = sol["path"]
                delta_tau = sol["objectives"]["trust"] / (sol["objectives"]["latency"] / 20.0 + 1e-3)
                for i in range(len(p) - 1):
                    u, v = p[i], p[i+1]
                    if (u, v) in self.pheromones:
                        self.pheromones[(u, v)] += delta_tau
                    if (v, u) in self.pheromones:
                        self.pheromones[(v, u)] += delta_tau
                        
            all_solutions.extend(iter_solutions)
            self.archive = extract_pareto_front(self.archive + iter_solutions)
            if len(self.archive) > 50:
                self.archive = random.sample(self.archive, 50)
                
        return {
            "pareto_front": self.archive,
            "best_compromise": topsis_selection(self.archive),
            "eval_count": eval_count
        }

# -------------------------------------------------------------
# 6. Multi-Objective Evolutionary Algorithm by Decomposition (MOEA/D)
# -------------------------------------------------------------
class MOEADBaseline:
    def __init__(self, encoder_decoder, pop_size=40, max_iter=40, T_neighbors=5, 
                 crossover_rate=0.85, mutation_rate=0.15, seed=42):
        self.encoder_decoder = encoder_decoder
        self.graph = encoder_decoder.graph
        self.num_nodes = encoder_decoder.num_nodes
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.T_neighbors = min(T_neighbors, pop_size)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Generate uniform weight vectors for 4 objectives
        raw_weights = np.random.dirichlet(np.ones(4), size=pop_size)
        self.weights = raw_weights / np.sum(raw_weights, axis=1, keepdims=True)
        
        # Compute Euclidean distance between weight vectors to establish neighborhoods
        dists = np.linalg.norm(self.weights[:, None, :] - self.weights[None, :, :], axis=2)
        self.neighborhoods = np.argsort(dists, axis=1)[:, :self.T_neighbors]
        
    def _tchebycheff(self, norm_objs, weight_vec, ideal_point):
        # Objectives standardized to minimization: ideal_point = 0.0
        return np.max(weight_vec * np.abs(norm_objs - ideal_point))

    def optimize(self, source, destination):
        bounds = {"latency": (5.0, 120.0), "energy": (0.5, 15.0)}
        from src.evaluation.metrics import normalize_objectives
        
        # Initialize population
        X = np.random.uniform(0.0, 1.0, size=(self.pop_size, self.num_nodes))
        solutions = []
        eval_count = 0
        
        for i in range(self.pop_size):
            path = self.encoder_decoder.decode(X[i], source, destination)
            objs = self.encoder_decoder.evaluate_objectives(path)
            eval_count += 1
            solutions.append({"position": X[i].copy(), "path": path, "objectives": objs})
            
        # Ideal objective point (standardized minimization -> best is ideal_point 0.0)
        ideal_point = np.zeros(4)
        archive = extract_pareto_front(solutions)
        
        for t in range(self.max_iter):
            for i in range(self.pop_size):
                # Pick two parents from neighborhood B(i)
                nbrs = self.neighborhoods[i]
                p1, p2 = np.random.choice(nbrs, size=2, replace=False)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    mask = np.random.rand(self.num_nodes) < 0.5
                    y = np.where(mask, X[p1], X[p2])
                else:
                    y = X[p1].copy()
                    
                # Mutation
                if random.random() < self.mutation_rate:
                    mut_mask = np.random.rand(self.num_nodes) < 0.10
                    y[mut_mask] = np.random.uniform(0.0, 1.0, size=np.sum(mut_mask))
                    
                y = np.clip(y, 0.0, 1.0)
                path = self.encoder_decoder.decode(y, source, destination)
                objs = self.encoder_decoder.evaluate_objectives(path)
                eval_count += 1
                
                new_sol = {"position": y, "path": path, "objectives": objs}
                norm_y = 1.0 - normalize_objectives(objs, bounds) # minimization
                
                # Update neighbors
                for j in nbrs:
                    norm_curr = 1.0 - normalize_objectives(solutions[j]["objectives"], bounds)
                    g_y = self._tchebycheff(norm_y, self.weights[j], ideal_point)
                    g_curr = self._tchebycheff(norm_curr, self.weights[j], ideal_point)
                    if g_y < g_curr:
                        X[j] = y.copy()
                        solutions[j] = new_sol
                        
                archive = extract_pareto_front(archive + [new_sol])
                if len(archive) > 50:
                    archive = random.sample(archive, 50)
                    
        return {
            "pareto_front": archive,
            "best_compromise": topsis_selection(archive),
            "eval_count": eval_count
        }

# -------------------------------------------------------------
# 7. Strength Pareto Evolutionary Algorithm 2 (SPEA2)
# -------------------------------------------------------------
class SPEA2Baseline:
    def __init__(self, encoder_decoder, pop_size=40, max_iter=40, archive_capacity=40,
                 crossover_rate=0.85, mutation_rate=0.15, seed=42):
        self.encoder_decoder = encoder_decoder
        self.graph = encoder_decoder.graph
        self.num_nodes = encoder_decoder.num_nodes
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.archive_capacity = archive_capacity
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def optimize(self, source, destination):
        bounds = {"latency": (5.0, 120.0), "energy": (0.5, 15.0)}
        from src.evaluation.metrics import normalize_objectives
        
        # Initialize population
        X = np.random.uniform(0.0, 1.0, size=(self.pop_size, self.num_nodes))
        pop = []
        eval_count = 0
        
        for i in range(self.pop_size):
            path = self.encoder_decoder.decode(X[i], source, destination)
            objs = self.encoder_decoder.evaluate_objectives(path)
            eval_count += 1
            pop.append({"position": X[i].copy(), "path": path, "objectives": objs})
            
        archive = []
        
        for t in range(self.max_iter):
            union = pop + archive
            n_union = len(union)
            
            # Extract normalized objective vectors (minimization standard)
            norm_matrix = np.array([1.0 - normalize_objectives(sol["objectives"], bounds) for sol in union])
            
            # 1. Strength S(i)
            # S(i) = count of solutions in union that solution i dominates
            strength = np.zeros(n_union)
            for i in range(n_union):
                for j in range(n_union):
                    if i != j and dominates(union[i]["objectives"], union[j]["objectives"]):
                        strength[i] += 1
                        
            # 2. Raw Fitness R(i)
            # R(i) = sum of strengths of solutions that dominate i
            raw_fitness = np.zeros(n_union)
            for i in range(n_union):
                for j in range(n_union):
                    if i != j and dominates(union[j]["objectives"], union[i]["objectives"]):
                        raw_fitness[i] += strength[j]
                        
            # 3. Density estimation D(i) via k-th nearest neighbor
            k_nn = int(math.sqrt(n_union))
            dists = np.linalg.norm(norm_matrix[:, None, :] - norm_matrix[None, :, :], axis=2)
            sorted_dists = np.sort(dists, axis=1)
            sigma_k = sorted_dists[:, k_nn] if k_nn < n_union else sorted_dists[:, -1]
            density = 1.0 / (sigma_k + 2.0)
            
            fitness = raw_fitness + density
            
            # Environmental selection: non-dominated solutions have fitness < 1.0
            nd_indices = np.where(fitness < 1.0)[0]
            if len(nd_indices) <= self.archive_capacity:
                # Add best dominated solutions until archive capacity
                sorted_fit_indices = np.argsort(fitness)
                archive_indices = list(sorted_fit_indices[:self.archive_capacity])
            else:
                # Truncate using nearest neighbor distance
                nd_dists = dists[np.ix_(nd_indices, nd_indices)]
                np.fill_diagonal(nd_dists, np.inf)
                rem_indices = list(nd_indices)
                while len(rem_indices) > self.archive_capacity:
                    min_d = np.min(nd_dists, axis=1)
                    worst_rel_idx = int(np.argmin(min_d))
                    rem_indices.pop(worst_rel_idx)
                    nd_dists = np.delete(np.delete(nd_dists, worst_rel_idx, axis=0), worst_rel_idx, axis=1)
                archive_indices = rem_indices
                
            archive = [union[idx] for idx in archive_indices]
            archive_fitness = [fitness[idx] for idx in archive_indices]
            
            if t == self.max_iter - 1:
                break
                
            # Mating selection via binary tournament on archive
            mating_pool = []
            for _ in range(self.pop_size):
                i1, i2 = random.sample(range(len(archive)), 2)
                f1 = archive_fitness[i1]
                f2 = archive_fitness[i2]
                mating_pool.append(archive[i1] if f1 < f2 else archive[i2])
                
            # Recombination & Mutation to produce new population
            new_pop = []
            new_X = np.zeros((self.pop_size, self.num_nodes))
            for i in range(0, self.pop_size, 2):
                p1 = mating_pool[i]["position"]
                p2 = mating_pool[(i + 1) % self.pop_size]["position"]
                
                # Crossover
                if random.random() < self.crossover_rate:
                    mask = np.random.rand(self.num_nodes) < 0.5
                    c1 = np.where(mask, p1, p2)
                    c2 = np.where(mask, p2, p1)
                else:
                    c1, c2 = p1.copy(), p2.copy()
                    
                # Mutation
                for child, c_idx in [(c1, i), (c2, (i + 1) % self.pop_size)]:
                    if random.random() < self.mutation_rate:
                        mut_mask = np.random.rand(self.num_nodes) < 0.10
                        child[mut_mask] = np.random.uniform(0.0, 1.0, size=np.sum(mut_mask))
                    child = np.clip(child, 0.0, 1.0)
                    new_X[c_idx] = child
                    path = self.encoder_decoder.decode(child, source, destination)
                    objs = self.encoder_decoder.evaluate_objectives(path)
                    eval_count += 1
                    new_pop.append({"position": child, "path": path, "objectives": objs})
            pop = new_pop
            
        final_pareto = extract_pareto_front(archive)
        return {
            "pareto_front": final_pareto,
            "best_compromise": topsis_selection(final_pareto),
            "eval_count": eval_count
        }

# -------------------------------------------------------------
# 8. Canonical Multi-Objective Marine Predators Algorithm (MOMPA)
# -------------------------------------------------------------
class MOMPABaseline:
    def __init__(self, encoder_decoder, pop_size=40, max_iter=40, archive_capacity=40,
                 fads_prob=0.20, seed=42):
        self.encoder_decoder = encoder_decoder
        self.graph = encoder_decoder.graph
        self.num_nodes = encoder_decoder.num_nodes
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.archive_capacity = archive_capacity
        self.fads_prob = fads_prob
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.beta = 1.5
        num = math.gamma(1.0 + self.beta) * math.sin(math.pi * self.beta / 2.0)
        den = math.gamma((1.0 + self.beta) / 2.0) * self.beta * (2.0 ** ((self.beta - 1.0) / 2.0))
        self.sigma_u = (num / den) ** (1.0 / self.beta)

    def _sample_levy(self, size):
        u = np.random.normal(0, self.sigma_u, size=size)
        v = np.random.normal(0, 1, size=size)
        return 0.05 * (u / (np.abs(v) ** (1.0 / self.beta)))

    def optimize(self, source, destination):
        Prey = np.random.uniform(0.0, 1.0, size=(self.pop_size, self.num_nodes))
        archive = []
        eval_count = 0
        
        # Initial evaluation
        for i in range(self.pop_size):
            path = self.encoder_decoder.decode(Prey[i], source, destination)
            objs = self.encoder_decoder.evaluate_objectives(path)
            eval_count += 1
            archive.append({"position": Prey[i].copy(), "path": path, "objectives": objs})
            
        archive = extract_pareto_front(archive)
        
        for t in range(self.max_iter):
            progress = t / self.max_iter
            CF = (1.0 - progress) ** (2.0 * progress)
            P = 0.5
            
            # Select elite from archive
            Elite = random.choice(archive)["position"] if archive else Prey[0]
            new_Prey = np.zeros_like(Prey)
            
            # Velocity regimes
            if t < self.max_iter / 3:
                # Phase 1: High velocity ratio (Brownian)
                for i in range(self.pop_size):
                    RB = np.random.normal(0, 1, size=self.num_nodes)
                    R_rand = np.random.uniform(0, 1, size=self.num_nodes)
                    step = RB * (Elite - RB * Prey[i])
                    new_Prey[i] = Prey[i] + P * R_rand * step
            elif t < 2 * self.max_iter / 3:
                # Phase 2: Unit velocity ratio (Lévy + Brownian)
                half = self.pop_size // 2
                for i in range(half):
                    RL = self._sample_levy(self.num_nodes)
                    R_rand = np.random.uniform(0, 1, size=self.num_nodes)
                    step = RL * (Elite - RL * Prey[i])
                    new_Prey[i] = Prey[i] + P * R_rand * step
                for i in range(half, self.pop_size):
                    RB = np.random.normal(0, 1, size=self.num_nodes)
                    step = RB * (RB * Elite - Prey[i])
                    new_Prey[i] = Elite + P * CF * step
            else:
                # Phase 3: Low velocity ratio (Lévy predator)
                for i in range(self.pop_size):
                    RL = self._sample_levy(self.num_nodes)
                    step = RL * (RL * Elite - Prey[i])
                    new_Prey[i] = Elite + P * CF * step
                    
            # FADs effect
            for i in range(self.pop_size):
                if random.random() <= self.fads_prob:
                    U = (np.random.uniform(0, 1, size=self.num_nodes) < self.fads_prob).astype(float)
                    R_rand = np.random.uniform(0, 1, size=self.num_nodes)
                    new_Prey[i] += CF * (R_rand * 1.0) * U
                else:
                    r1 = random.randint(0, self.pop_size - 1)
                    r2 = random.randint(0, self.pop_size - 1)
                    r_rand = random.random()
                    new_Prey[i] += (self.fads_prob * (1.0 - r_rand) + r_rand) * (Prey[r1] - Prey[r2])
                    
            new_Prey = np.clip(new_Prey, 0.0, 1.0)
            iter_solutions = []
            for i in range(self.pop_size):
                path = self.encoder_decoder.decode(new_Prey[i], source, destination)
                objs = self.encoder_decoder.evaluate_objectives(path)
                eval_count += 1
                iter_solutions.append({"position": new_Prey[i].copy(), "path": path, "objectives": objs})
                
            archive = extract_pareto_front(archive + iter_solutions)
            if len(archive) > self.archive_capacity:
                archive = random.sample(archive, self.archive_capacity)
            Prey = new_Prey.copy()
            
        return {
            "pareto_front": archive,
            "best_compromise": topsis_selection(archive),
            "eval_count": eval_count
        }

# -------------------------------------------------------------
# 9. Published SIoT Trust Model 1: Beta-Reputation System
# -------------------------------------------------------------
class BetaReputationTrustModel:
    """
    Canonical Bayesian Beta-Reputation framework with outlier filtering
    (Josang & Haller, 2007; Chen et al., 2016).
    """
    def __init__(self, outlier_threshold=1.96):
        self.outlier_threshold = outlier_threshold

    def compute_trust(self, successes, failures, recommendations=None):
        alpha = successes + 1.0
        beta_param = failures + 1.0
        direct_trust = alpha / (alpha + beta_param)
        
        if not recommendations:
            return float(direct_trust)
            
        ratings = list(recommendations.values())
        if len(ratings) <= 1:
            return float(0.6 * direct_trust + 0.4 * (ratings[0] if ratings else 0.5))
            
        mean_r = np.mean(ratings)
        std_r = np.std(ratings)
        
        # Outlier filtering: discard recommendations > 1.96 sigma away from mean
        filtered = [r for r in ratings if abs(r - mean_r) <= self.outlier_threshold * max(std_r, 0.05)]
        ind_trust = float(np.mean(filtered)) if filtered else float(mean_r)
        
        # Bayesian fusion: 60% direct evidence, 40% indirect consensus
        return float(np.clip(0.60 * direct_trust + 0.40 * ind_trust, 0.0, 1.0))

# -------------------------------------------------------------
# 10. Published SIoT Trust Model 2: EigenTrust Model
# -------------------------------------------------------------
class EigenTrustModel:
    """
    Canonical EigenTrust power iteration algorithm for peer-to-peer and SIoT networks
    (Kamvar et al., 2003; Marche et al., 2020).
    """
    def __init__(self, pre_trusted_weight=0.15, max_iter=20, tol=1e-4):
        self.alpha = pre_trusted_weight
        self.max_iter = max_iter
        self.tol = tol

    def compute_global_trust(self, graph, direct_trust_dict):
        nodes = sorted(list(graph.nodes()))
        N = len(nodes)
        if N == 0:
            return {}
            
        node_to_idx = {n: i for i, n in enumerate(nodes)}
        C = np.zeros((N, N))
        
        for (u, v), t in direct_trust_dict.items():
            if u in node_to_idx and v in node_to_idx:
                C[node_to_idx[u], node_to_idx[v]] = max(0.0, t)
                
        # Normalize rows to form transition probability matrix
        row_sums = np.sum(C, axis=1, keepdims=True)
        # Uniform fallback for dead ends
        uniform_row = np.ones(N) / N
        C = np.where(row_sums > 1e-9, C / (row_sums + 1e-9), uniform_row)
        
        # Pre-trusted uniform vector p
        p = np.ones(N) / N
        t_vec = p.copy()
        
        # Power iteration
        for _ in range(self.max_iter):
            t_next = (1.0 - self.alpha) * (C.T @ t_vec) + self.alpha * p
            if np.linalg.norm(t_next - t_vec, 1) < self.tol:
                break
            t_vec = t_next
            
        # Scale to [0, 1]
        t_max = np.max(t_vec)
        t_scaled = t_vec / (t_max + 1e-9) if t_max > 0 else t_vec
        return {nodes[i]: float(t_scaled[i]) for i in range(N)}

