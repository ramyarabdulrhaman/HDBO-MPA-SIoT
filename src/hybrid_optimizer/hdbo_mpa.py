"""
Hybrid Dung Beetle Optimization and Marine Predators Algorithm (HDBO-MPA).
A Co-Evolutionary Multi-Objective Metaheuristic for Trust-Aware Service Discovery in Social IoT.
Combines DBO's multi-role exploratory divergence with MPA's scale-free Lévy-Brownian exploitation
via a shared non-dominated Pareto archive and dynamic operator adaptation.
"""

import math
import random
import numpy as np
from src.evaluation.metrics import (
    dominates, extract_pareto_front, compute_hypervolume, topsis_selection
)

class HDBOMPAOptimizer:
    def __init__(self, encoder_decoder, pop_size=40, max_iter=40, archive_capacity=40, 
                 dbo_ratio=0.50, fads_prob=0.20, sequential=False, no_crowding=False,
                 random_key_only=False, no_loop_erasure=False, seed=42):
        self.encoder_decoder = encoder_decoder
        self.num_nodes = encoder_decoder.num_nodes
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.archive_capacity = archive_capacity
        self.dbo_ratio = dbo_ratio
        self.fads_prob = fads_prob
        self.sequential = sequential
        self.no_crowding = no_crowding
        self.random_key_only = random_key_only
        self.no_loop_erasure = no_loop_erasure
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.n_dbo = int(pop_size * dbo_ratio)
        self.n_mpa = pop_size - self.n_dbo
        
        self.n_roll = int(self.n_dbo * 0.40)
        self.n_breed = int(self.n_dbo * 0.40)
        self.n_steal = self.n_dbo - (self.n_roll + self.n_breed)
        
        self.archive = [] # Shared Non-Dominated External Pareto Archive
        
        self.beta = 1.5
        num = math.gamma(1.0 + self.beta) * math.sin(math.pi * self.beta / 2.0)
        den = math.gamma((1.0 + self.beta) / 2.0) * self.beta * (2.0 ** ((self.beta - 1.0) / 2.0))
        self.sigma_u = (num / den) ** (1.0 / self.beta)

    def _sample_levy(self, size):
        u = np.random.normal(0, self.sigma_u, size=size)
        v = np.random.normal(0, 1, size=size)
        return 0.05 * (u / (np.abs(v) ** (1.0 / self.beta)))

    def _crowding_distance_pruning(self, archive, target_size):
        if len(archive) <= target_size:
            return archive
        if self.no_crowding:
            # Ablation A10: Random archive pruning without crowding distance
            return random.sample(archive, target_size)
            
        n = len(archive)
        distances = np.zeros(n)
        for key in ["trust", "latency", "energy", "qos"]:
            vals = [sol["objectives"][key] for sol in archive]
            sorted_idx = np.argsort(vals)
            distances[sorted_idx[0]] = 1e9
            distances[sorted_idx[-1]] = 1e9
            val_range = vals[sorted_idx[-1]] - vals[sorted_idx[0]]
            if val_range > 1e-9:
                for i in range(1, n - 1):
                    distances[sorted_idx[i]] += (vals[sorted_idx[i+1]] - vals[sorted_idx[i-1]]) / val_range
        survivors_idx = np.argsort(distances)[::-1][:target_size]
        return [archive[i] for i in sorted(survivors_idx)]

    def _update_archive(self, candidates):
        combined = self.archive + candidates
        self.archive = extract_pareto_front(combined)
        if len(self.archive) > self.archive_capacity:
            self.archive = self._crowding_distance_pruning(self.archive, self.archive_capacity)

    def optimize(self, source, destination, track_convergence=False):
        """
        Executes HDBO-MPA multi-objective optimization.
        """
        X_dbo = np.random.uniform(0.0, 1.0, size=(self.n_dbo, self.num_nodes))
        X_dbo_prev = X_dbo.copy()
        X_mpa = np.random.uniform(0.0, 1.0, size=(self.n_mpa, self.num_nodes))
        
        initial_solutions = []
        for i in range(self.n_dbo):
            path = self.encoder_decoder.decode(
                X_dbo[i], source, destination, 
                random_key_only=self.random_key_only, no_loop_erasure=self.no_loop_erasure
            )
            objs = self.encoder_decoder.evaluate_objectives(path)
            initial_solutions.append({"position": X_dbo[i], "path": path, "objectives": objs})
            
        for i in range(self.n_mpa):
            path = self.encoder_decoder.decode(
                X_mpa[i], source, destination,
                random_key_only=self.random_key_only, no_loop_erasure=self.no_loop_erasure
            )
            objs = self.encoder_decoder.evaluate_objectives(path)
            initial_solutions.append({"position": X_mpa[i], "path": path, "objectives": objs})
            
        self._update_archive(initial_solutions)
        eval_count = self.pop_size
        convergence_history = []
        
        last_size = len(self.archive)
        stagnation_counter = 0
        
        for t in range(self.max_iter):
            progress = t / self.max_iter
            R = 1.0 - progress
            CF = (1.0 - progress) ** (2.0 * progress)
            
            # Focused elite selection: pick among top compromise or diverse solutions from archive
            if self.archive:
                if len(self.archive) > 3 and not self.no_crowding:
                    top_k = self._crowding_distance_pruning(self.archive, max(3, len(self.archive) // 3))
                    best_sol = random.choice(top_k)
                else:
                    best_sol = random.choice(self.archive)
                X_best = best_sol["position"].copy()
            else:
                X_best = X_dbo[0].copy()
                
            X_worst = np.mean(np.vstack([X_dbo, X_mpa]), axis=0)
            
            # --- DBO Phase ---
            new_X_dbo = np.zeros_like(X_dbo)
            for i in range(self.n_roll):
                if random.random() < 0.70:
                    alpha = 1.0 if random.random() > 0.5 else -1.0
                    k = random.uniform(0.05, 0.20)
                    b = random.uniform(0.1, 0.9)
                    delta_x = np.abs(X_dbo[i] - X_worst)
                    new_X_dbo[i] = X_dbo[i] + alpha * k * X_dbo_prev[i] + b * delta_x
                else:
                    theta = random.uniform(0.0, math.pi)
                    tan_theta = math.tan(theta) if abs(theta - math.pi / 2) > 0.05 else 1.0
                    new_X_dbo[i] = X_dbo[i] + tan_theta * np.abs(X_dbo[i] - X_dbo_prev[i])
                    
            Lb_star = np.maximum(X_best * (1.0 - R), 0.0)
            Ub_star = np.minimum(X_best * (1.0 + R), 1.0)
            for i in range(self.n_roll, self.n_roll + self.n_breed):
                b1 = random.uniform(0.0, 1.0)
                b2 = random.uniform(0.0, 1.0)
                new_X_dbo[i] = X_best + b1 * (X_dbo[i] - Lb_star) + b2 * (X_dbo[i] - Ub_star)
                
            for i in range(self.n_roll + self.n_breed, self.n_dbo):
                g = np.random.normal(0, 1, size=self.num_nodes)
                new_X_dbo[i] = X_best + 0.5 * g * (np.abs(X_dbo[i] - X_best) + np.abs(X_dbo[i] - X_worst))
                
            # --- MPA Phase ---
            new_X_mpa = np.zeros_like(X_mpa)
            P = 0.5
            
            # Sequential hybrid check (A7)
            if self.sequential:
                if t < self.max_iter / 2:
                    # In first half, MPA agents also run DBO exploration
                    new_X_mpa = new_X_dbo.copy() if len(new_X_dbo) == len(new_X_mpa) else np.vstack([new_X_dbo, new_X_dbo])[:len(new_X_mpa)]
                else:
                    # In second half, run MPA
                    for i in range(self.n_mpa):
                        RL = self._sample_levy(self.num_nodes)
                        step = RL * (RL * X_best - X_mpa[i])
                        new_X_mpa[i] = X_best + P * CF * step
            else:
                if t < self.max_iter / 3:
                    for i in range(self.n_mpa):
                        RB = np.random.normal(0, 1, size=self.num_nodes)
                        R_rand = np.random.uniform(0, 1, size=self.num_nodes)
                        step_size = RB * (X_best - RB * X_mpa[i])
                        new_X_mpa[i] = X_mpa[i] + P * R_rand * step_size
                elif t < 2 * self.max_iter / 3:
                    half = self.n_mpa // 2
                    for i in range(half):
                        RL = self._sample_levy(self.num_nodes)
                        R_rand = np.random.uniform(0, 1, size=self.num_nodes)
                        step_size = RL * (X_best - RL * X_mpa[i])
                        new_X_mpa[i] = X_mpa[i] + P * R_rand * step_size
                    for i in range(half, self.n_mpa):
                        RB = np.random.normal(0, 1, size=self.num_nodes)
                        step_size = RB * (RB * X_best - X_mpa[i])
                        new_X_mpa[i] = X_best + P * CF * step_size
                else:
                    for i in range(self.n_mpa):
                        RL = self._sample_levy(self.num_nodes)
                        step_size = RL * (RL * X_best - X_mpa[i])
                        new_X_mpa[i] = X_best + P * CF * step_size
                        
                for i in range(self.n_mpa):
                    if random.random() <= self.fads_prob:
                        U = (np.random.uniform(0, 1, size=self.num_nodes) < self.fads_prob).astype(float)
                        R_rand = np.random.uniform(0, 1, size=self.num_nodes)
                        new_X_mpa[i] = new_X_mpa[i] + CF * (R_rand * 1.0) * U
                    else:
                        r1 = random.randint(0, self.n_mpa - 1)
                        r2 = random.randint(0, self.n_mpa - 1)
                        r_rand = random.random()
                        new_X_mpa[i] = new_X_mpa[i] + (self.fads_prob * (1.0 - r_rand) + r_rand) * (X_mpa[r1] - X_mpa[r2])
                        
            if stagnation_counter >= 3 and not self.sequential:
                n_exchange = max(1, self.n_mpa // 5)
                replace_indices = random.sample(range(self.n_mpa), n_exchange)
                donor_indices = random.sample(range(self.n_roll, self.n_roll + self.n_breed), n_exchange)
                for r_idx, d_idx in zip(replace_indices, donor_indices):
                    new_X_mpa[r_idx] = new_X_dbo[d_idx].copy()
                stagnation_counter = 0
                
            new_X_dbo = np.clip(new_X_dbo, 0.0, 1.0)
            new_X_mpa = np.clip(new_X_mpa, 0.0, 1.0)
            
            iter_solutions = []
            for i in range(self.n_dbo):
                path = self.encoder_decoder.decode(
                    new_X_dbo[i], source, destination,
                    random_key_only=self.random_key_only, no_loop_erasure=self.no_loop_erasure
                )
                objs = self.encoder_decoder.evaluate_objectives(path)
                iter_solutions.append({"position": new_X_dbo[i], "path": path, "objectives": objs})
                eval_count += 1
                
            for i in range(self.n_mpa):
                path = self.encoder_decoder.decode(
                    new_X_mpa[i], source, destination,
                    random_key_only=self.random_key_only, no_loop_erasure=self.no_loop_erasure
                )
                objs = self.encoder_decoder.evaluate_objectives(path)
                iter_solutions.append({"position": new_X_mpa[i], "path": path, "objectives": objs})
                eval_count += 1
                
            self._update_archive(iter_solutions)
            
            if len(self.archive) == last_size:
                stagnation_counter += 1
            else:
                stagnation_counter = 0
            last_size = len(self.archive)
            
            if track_convergence and (t % 5 == 0 or t == self.max_iter - 1):
                curr_hv = compute_hypervolume(self.archive, num_samples=1000)
                convergence_history.append({"iteration": t + 1, "eval_count": eval_count, "hv": curr_hv})
                
            X_dbo_prev = X_dbo.copy()
            X_dbo = new_X_dbo.copy()
            X_mpa = new_X_mpa.copy()
            
        best_operational = topsis_selection(self.archive)
        return {
            "pareto_front": self.archive,
            "best_compromise": best_operational,
            "eval_count": eval_count,
            "convergence_history": convergence_history
        }

