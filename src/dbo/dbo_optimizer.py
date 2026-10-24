"""
Dung Beetle Optimizer (DBO) adapted for Multi-Objective Combinatorial Service Discovery.
Implements canonical ball-rolling, dancing, breeding, foraging, and stealing behaviors
coupled with Pareto archive management and graph-constrained decoding.
"""

import math
import random
import numpy as np
from src.evaluation.metrics import dominates, extract_pareto_front

class DBOptimizer:
    def __init__(self, encoder_decoder, pop_size=40, max_iter=50, archive_capacity=50, seed=42):
        self.encoder_decoder = encoder_decoder
        self.num_nodes = encoder_decoder.num_nodes
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.archive_capacity = archive_capacity
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Partition population into 4 canonical DBO sub-groups
        self.n_roll = int(pop_size * 0.25)
        self.n_breed = int(pop_size * 0.25)
        self.n_forage = int(pop_size * 0.25)
        self.n_steal = pop_size - (self.n_roll + self.n_breed + self.n_forage)
        
        self.archive = [] # Non-dominated Pareto archive

    def _crowding_distance_pruning(self, archive, target_size):
        """
        Prunes archive to target_size using crowding distance to preserve diversity.
        """
        if len(archive) <= target_size:
            return archive
            
        n = len(archive)
        distances = np.zeros(n)
        
        # Calculate crowding distance across the 4 objectives
        for key in ["trust", "latency", "energy", "qos"]:
            vals = [sol["objectives"][key] for sol in archive]
            sorted_idx = np.argsort(vals)
            distances[sorted_idx[0]] = 1e9
            distances[sorted_idx[-1]] = 1e9
            val_range = vals[sorted_idx[-1]] - vals[sorted_idx[0]]
            if val_range > 1e-9:
                for i in range(1, n - 1):
                    distances[sorted_idx[i]] += (vals[sorted_idx[i+1]] - vals[sorted_idx[i-1]]) / val_range
                    
        # Retain solutions with largest crowding distances
        survivors_idx = np.argsort(distances)[::-1][:target_size]
        return [archive[i] for i in sorted(survivors_idx)]

    def _update_archive(self, candidates):
        """
        Updates the non-dominated Pareto archive with new candidates.
        """
        combined = self.archive + candidates
        self.archive = extract_pareto_front(combined)
        if len(self.archive) > self.archive_capacity:
            self.archive = self._crowding_distance_pruning(self.archive, self.archive_capacity)

    def optimize(self, source, destination):
        """
        Executes DBO multi-objective optimization for discovering Pareto service paths.
        """
        # 1. Initialize population uniformly in [0, 1]^D
        X = np.random.uniform(0.0, 1.0, size=(self.pop_size, self.num_nodes))
        X_prev = X.copy()
        
        # Evaluate initial population
        solutions = []
        for i in range(self.pop_size):
            path = self.encoder_decoder.decode(X[i], source, destination)
            objs = self.encoder_decoder.evaluate_objectives(path)
            solutions.append({"position": X[i], "path": path, "objectives": objs})
            
        self._update_archive(solutions)
        
        history_hv = []
        eval_count = self.pop_size
        
        # Iteration Loop
        for t in range(self.max_iter):
            R = 1.0 - (t / self.max_iter) # Decreasing exploration ratio
            
            # Select current best and worst reference positions from archive
            if self.archive:
                best_sol = random.choice(self.archive)
                X_best = best_sol["position"].copy()
            else:
                X_best = X[0].copy()
            X_worst = np.mean(X, axis=0) # Centroid / worst estimation
            
            new_X = np.zeros_like(X)
            
            # --- 1. Ball-Rolling Subgroup (i = 0 ... n_roll-1) ---
            for i in range(self.n_roll):
                r_obst = random.random()
                if r_obst < 0.70:
                    # Rolling without obstacle (celestial navigation)
                    alpha = 1.0 if random.random() > 0.5 else -1.0
                    k = random.uniform(0.05, 0.20)
                    b = random.uniform(0.1, 0.9)
                    delta_x = np.abs(X[i] - X_worst)
                    new_X[i] = X[i] + alpha * k * X_prev[i] + b * delta_x
                else:
                    # Dancing behavior upon encountering obstacle
                    theta = random.uniform(0.0, math.pi)
                    if abs(theta - math.pi / 2) > 0.05:
                        tan_theta = math.tan(theta)
                    else:
                        tan_theta = 1.0
                    new_X[i] = X[i] + tan_theta * np.abs(X[i] - X_prev[i])
                    
            # --- 2. Breeding Subgroup (i = n_roll ... n_roll + n_breed - 1) ---
            Lb_star = np.maximum(X_best * (1.0 - R), 0.0)
            Ub_star = np.minimum(X_best * (1.0 + R), 1.0)
            idx_start = self.n_roll
            idx_end = self.n_roll + self.n_breed
            for i in range(idx_start, idx_end):
                b1 = random.uniform(0.0, 1.0)
                b2 = random.uniform(0.0, 1.0)
                new_X[i] = X_best + b1 * (X[i] - Lb_star) + b2 * (X[i] - Ub_star)
                
            # --- 3. Foraging Subgroup (i = idx_end ... idx_end + n_forage - 1) ---
            Lb_b = np.maximum(X_best * (1.0 - R), 0.0)
            Ub_b = np.minimum(X_best * (1.0 + R), 1.0)
            idx_f_start = idx_end
            idx_f_end = idx_end + self.n_forage
            for i in range(idx_f_start, idx_f_end):
                C1 = np.random.uniform(0.0, 1.0, size=self.num_nodes)
                C2 = np.random.uniform(0.0, 1.0, size=self.num_nodes)
                new_X[i] = X[i] + C1 * (X[i] - Lb_b) + C2 * (X[i] - Ub_b)
                
            # --- 4. Stealing Subgroup (i = idx_f_end ... pop_size - 1) ---
            for i in range(idx_f_end, self.pop_size):
                g = np.random.normal(0, 1, size=self.num_nodes)
                S = 0.5
                new_X[i] = X_best + S * g * (np.abs(X[i] - X_best) + np.abs(X[i] - X_worst))
                
            # Boundary handling: clip to [0, 1]
            new_X = np.clip(new_X, 0.0, 1.0)
            
            # Evaluate new population and update archive
            iter_solutions = []
            for i in range(self.pop_size):
                path = self.encoder_decoder.decode(new_X[i], source, destination)
                objs = self.encoder_decoder.evaluate_objectives(path)
                iter_solutions.append({"position": new_X[i], "path": path, "objectives": objs})
                eval_count += 1
                
            self._update_archive(iter_solutions)
            
            X_prev = X.copy()
            X = new_X.copy()
            
        return {
            "pareto_front": self.archive,
            "eval_count": eval_count,
            "runtime_iterations": self.max_iter
        }
