"""
Marine Predators Algorithm (MPA) adapted for Multi-Objective Combinatorial Service Discovery.
Implements canonical 3-phase velocity transitions (Brownian exploration, Eddy foraging, Lévy exploitation),
Fish Aggregating Devices (FADs) effect, and Pareto archive management.
"""

import math
import random
import numpy as np
from src.evaluation.metrics import dominates, extract_pareto_front

class MPAOptimizer:
    def __init__(self, encoder_decoder, pop_size=40, max_iter=50, archive_capacity=50, seed=42):
        self.encoder_decoder = encoder_decoder
        self.num_nodes = encoder_decoder.num_nodes
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.archive_capacity = archive_capacity
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.archive = [] # Non-dominated Pareto archive
        
        # Precompute Mantegna Lévy flight parameters (beta = 1.5)
        self.beta = 1.5
        num = math.gamma(1.0 + self.beta) * math.sin(math.pi * self.beta / 2.0)
        den = math.gamma((1.0 + self.beta) / 2.0) * self.beta * (2.0 ** ((self.beta - 1.0) / 2.0))
        self.sigma_u = (num / den) ** (1.0 / self.beta)

    def _sample_levy(self, size):
        """
        Samples scale-free Lévy flight steps via Mantegna's algorithm.
        """
        u = np.random.normal(0, self.sigma_u, size=size)
        v = np.random.normal(0, 1, size=size)
        step = u / (np.abs(v) ** (1.0 / self.beta))
        return 0.05 * step

    def _crowding_distance_pruning(self, archive, target_size):
        if len(archive) <= target_size:
            return archive
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

    def optimize(self, source, destination):
        """
        Executes MPA multi-objective optimization for discovering Pareto service paths.
        """
        # Initialize Prey matrix
        Prey = np.random.uniform(0.0, 1.0, size=(self.pop_size, self.num_nodes))
        
        # Initial evaluation
        solutions = []
        for i in range(self.pop_size):
            path = self.encoder_decoder.decode(Prey[i], source, destination)
            objs = self.encoder_decoder.evaluate_objectives(path)
            solutions.append({"position": Prey[i], "path": path, "objectives": objs})
            
        self._update_archive(solutions)
        eval_count = self.pop_size
        
        P = 0.5
        FADs = 0.2
        
        for t in range(self.max_iter):
            # Construct Elite matrix from archive
            Elite = np.zeros_like(Prey)
            if self.archive:
                for i in range(self.pop_size):
                    chosen = random.choice(self.archive)
                    Elite[i] = chosen["position"].copy()
            else:
                Elite = Prey.copy()
                
            CF = (1.0 - (t / self.max_iter)) ** (2.0 * t / self.max_iter)
            new_Prey = np.zeros_like(Prey)
            
            # --- Phase 1: High Velocity Ratio (t < max_iter / 3) ---
            if t < self.max_iter / 3:
                for i in range(self.pop_size):
                    RB = np.random.normal(0, 1, size=self.num_nodes) # Brownian
                    R = np.random.uniform(0, 1, size=self.num_nodes)
                    step_size = RB * (Elite[i] - RB * Prey[i])
                    new_Prey[i] = Prey[i] + P * R * step_size
                    
            # --- Phase 2: Unit Velocity Ratio (max_iter / 3 <= t < 2 * max_iter / 3) ---
            elif t < 2 * self.max_iter / 3:
                half = self.pop_size // 2
                # First half: Lévy flight
                for i in range(half):
                    RL = self._sample_levy(self.num_nodes)
                    R = np.random.uniform(0, 1, size=self.num_nodes)
                    step_size = RL * (Elite[i] - RL * Prey[i])
                    new_Prey[i] = Prey[i] + P * R * step_size
                # Second half: Brownian motion
                for i in range(half, self.pop_size):
                    RB = np.random.normal(0, 1, size=self.num_nodes)
                    step_size = RB * (RB * Elite[i] - Prey[i])
                    new_Prey[i] = Elite[i] + P * CF * step_size
                    
            # --- Phase 3: Low Velocity Ratio (t >= 2 * max_iter / 3) ---
            else:
                for i in range(self.pop_size):
                    RL = self._sample_levy(self.num_nodes)
                    step_size = RL * (RL * Elite[i] - Prey[i])
                    new_Prey[i] = Elite[i] + P * CF * step_size
                    
            # --- Fish Aggregating Devices (FADs) Effect ---
            for i in range(self.pop_size):
                if random.random() <= FADs:
                    U = (np.random.uniform(0, 1, size=self.num_nodes) < FADs).astype(float)
                    R = np.random.uniform(0, 1, size=self.num_nodes)
                    new_Prey[i] = new_Prey[i] + CF * (0.0 + R * (1.0 - 0.0)) * U
                else:
                    r1 = random.randint(0, self.pop_size - 1)
                    r2 = random.randint(0, self.pop_size - 1)
                    r_rand = random.random()
                    new_Prey[i] = new_Prey[i] + (FADs * (1.0 - r_rand) + r_rand) * (Prey[r1] - Prey[r2])
                    
            new_Prey = np.clip(new_Prey, 0.0, 1.0)
            
            # Evaluate new Prey population
            iter_solutions = []
            for i in range(self.pop_size):
                path = self.encoder_decoder.decode(new_Prey[i], source, destination)
                objs = self.encoder_decoder.evaluate_objectives(path)
                iter_solutions.append({"position": new_Prey[i], "path": path, "objectives": objs})
                eval_count += 1
                
            self._update_archive(iter_solutions)
            Prey = new_Prey.copy()
            
        return {
            "pareto_front": self.archive,
            "eval_count": eval_count,
            "runtime_iterations": self.max_iter
        }
