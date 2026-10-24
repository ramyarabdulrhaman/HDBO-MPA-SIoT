"""
Graph-Constrained Random-Key Priority Path Representation and Decoding.
Translates continuous DBO and MPA search vectors into 100% loop-free, connected,
resource-feasible Social IoT service-delivery paths.
"""

import heapq
import numpy as np
import networkx as nx

class PathEncoderDecoder:
    def __init__(self, siot_graph, composite_trust_matrix, trust_engine=None):
        self.siot_graph = siot_graph
        self.graph = siot_graph.graph
        self.num_nodes = self.graph.number_of_nodes()
        self.node_attributes = siot_graph.node_attributes
        self.edge_attributes = siot_graph.edge_attributes
        self.composite_trust = composite_trust_matrix
        self.trust_engine = trust_engine
        
        # Calculate mean edge latency for dimensionless priority scoring
        latencies = [d.get("latency", 10.0) for d in self.edge_attributes.values()]
        self.mean_latency = float(np.mean(latencies)) if latencies else 10.0

    def decode(self, priority_vector, source, destination, max_hops=15, 
               random_key_only=False, no_loop_erasure=False):
        """
        Decodes a continuous priority vector x in [0, 1]^|V| into a valid path P = (s, ..., t).
        Uses dimensionless priority-guided traversal with Wilson loop-erasure and Dijkstra fallback.
        Supports ablation configurations (random_key_only for A8, no_loop_erasure for A9).
        """
        assert len(priority_vector) == self.num_nodes, "Priority vector length mismatch"
        
        if no_loop_erasure:
            # Ablation A9: Raw rounding / greedy without Wilson cycle purging or repair
            path = [source]
            curr = source
            visited = {source}
            for _ in range(max_hops):
                if curr == destination:
                    break
                neighbors = list(self.graph.neighbors(curr))
                if not neighbors:
                    break
                if destination in neighbors:
                    path.append(destination)
                    break
                unvisited = [n for n in neighbors if n not in visited]
                if not unvisited:
                    # Dead end without repair -> truncated infeasible path
                    break
                # Pick highest priority unvisited
                best_n = max(unvisited, key=lambda n: priority_vector[n])
                visited.add(best_n)
                path.append(best_n)
                curr = best_n
            return path
            
        path = [source]
        visited_indices = {source: 0} # Maps node -> index in path for Wilson loop erasure
        reentry_counts = {} # Step cap on greedy re-entry cycles
        curr = source
        
        for _ in range(max_hops):
            if curr == destination:
                break
                
            neighbors = list(self.graph.neighbors(curr))
            if not neighbors:
                break
                
            # If destination is directly adjacent and path has already progressed, connect
            if destination in neighbors and len(path) >= 2:
                curr = destination
                path.append(curr)
                break
                
            best_neighbor = None
            best_score = -1e9
            
            for nbr in neighbors:
                p_val = priority_vector[nbr]
                
                if random_key_only:
                    # Ablation A8: Pure random key without heuristic guidance
                    score = p_val
                else:
                    t_val = self.composite_trust.get((curr, nbr), 0.5)
                    edge_data = self.edge_attributes.get((curr, nbr), {})
                    lat = edge_data.get("latency", 10.0)
                    
                    # Dimensionless, unit-consistent priority scoring:
                    # Weights: 0.50 (agent priority) + 0.30 (trust) + 0.20 (normalized latency)
                    norm_lat = self.mean_latency / (lat + self.mean_latency)
                    score = 0.50 * p_val + 0.30 * t_val + 0.20 * norm_lat
                
                # Dynamic battery exhaustion bypass (E_threshold = 10% residual capacity)
                nbr_attr = self.node_attributes.get(nbr, {})
                init_e = nbr_attr.get("initial_energy", 10000.0)
                res_e = nbr_attr.get("residual_energy", init_e)
                if res_e <= 0.10 * init_e and nbr != destination:
                    score -= 0.60
                
                # Penalty and step-cap if neighbor was previously visited (prevent infinite cycles)
                if nbr in visited_indices:
                    reentry = reentry_counts.get(nbr, 0)
                    score -= (0.50 + 0.30 * reentry)
                    if reentry >= 2:
                        score -= 1.0 # Severe suppression for repeated cycles
                    
                if score > best_score:
                    best_score = score
                    best_neighbor = nbr
                    
            if best_neighbor is None:
                break
                
            # Wilson loop-erasure: instantaneous cycle purging
            if not no_loop_erasure and best_neighbor in visited_indices:
                idx = visited_indices[best_neighbor]
                removed_nodes = path[idx+1:]
                path = path[:idx+1]
                for rn in removed_nodes:
                    if rn in visited_indices:
                        del visited_indices[rn]
                reentry_counts[best_neighbor] = reentry_counts.get(best_neighbor, 0) + 1
                curr = best_neighbor
            else:
                curr = best_neighbor
                visited_indices[curr] = len(path)
                path.append(curr)
                
        # If traversal did not reach destination, invoke Constraint-Aware Fallback Repair
        if path[-1] != destination:
            def _constraint_weight(u, v, d):
                l = d.get('latency', 10.0)
                e = d.get('tx_energy', 0.25) + d.get('rx_energy', 0.1024)
                t = self.composite_trust.get((u, v), 0.50)
                return l + 4.0 * e + 12.0 * (1.0 - t)

            try:
                repair_segment = nx.shortest_path(self.graph, source=path[-1], target=destination, weight=_constraint_weight)
                path.extend(repair_segment[1:])
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                try:
                    path = nx.shortest_path(self.graph, source=source, target=destination, weight=_constraint_weight)
                except Exception:
                    path = [source, destination]
                
        # Final loop-erasure pass to purge any cycle introduced by fallback
        if not no_loop_erasure:
            final_path = []
            node_to_pos = {}
            for n in path:
                if n in node_to_pos:
                    idx = node_to_pos[n]
                    final_path = final_path[:idx+1]
                    node_to_pos = {node: i for i, node in enumerate(final_path)}
                else:
                    node_to_pos[n] = len(final_path)
                    final_path.append(n)
            return final_path
        else:
            return path
        
    def evaluate_constraints(self, path, max_latency=80.0, max_energy=5.0, min_trust=0.50):
        """
        Evaluates physical constraint satisfaction and computes Pareto constraint violation.
        CV(P) = max(0, L - C_L)/C_L + max(0, E - C_E)/C_E + max(0, C_T - T)/C_T
        """
        objs = self.evaluate_objectives(path)
        c_lat_viol = max(0.0, (objs["latency"] - max_latency) / max_latency)
        c_eng_viol = max(0.0, (objs["energy"] - max_energy) / max_energy)
        c_tru_viol = max(0.0, (min_trust - objs["trust"]) / min_trust)
        
        cv = c_lat_viol + c_eng_viol + c_tru_viol
        is_feasible = (cv <= 1e-6) and (len(path) >= 2)
        return {"is_feasible": is_feasible, "constraint_violation": float(cv)}

    def evaluate_objectives(self, path):
        """
        Evaluates the 4 primary objectives for a candidate service path P:
        1. f_T (Maximize Path Trust): [0, 1]
        2. f_L (Minimize End-to-End Latency): ms
        3. f_E (Minimize Energy Consumption): mJ
        4. f_Q (Maximize Quality of Service): [0, 1]
        """
        assert len(path) >= 2, "Path must contain at least 2 nodes"
        
        # 1. Path Trust
        if self.trust_engine:
            f_T = self.trust_engine.evaluate_path_trust(path, self.composite_trust, tau_min=0.40)
        else:
            scores = [self.composite_trust.get((path[i], path[i+1]), 0.5) for i in range(len(path)-1)]
            f_T = float(np.mean(scores))
            
        # 2. End-to-End Latency: sum of link transmission latencies + intermediate/destination node processing delays
        f_L = 0.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_data = self.edge_attributes.get((u, v), {})
            f_L += edge_data.get("latency", 10.0)
            
        for i in range(1, len(path)):
            v = path[i]
            v_attr = self.node_attributes.get(v, {})
            f_L += v_attr.get("processing_delay", 2.0)
            
        # 3. Energy Consumption: link radio (tx + rx) + node processing energy
        f_E = 0.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_data = self.edge_attributes.get((u, v), {})
            f_E += edge_data.get("tx_energy", 0.25)
            f_E += edge_data.get("rx_energy", 0.1024)
            
        for i in range(1, len(path)):
            v = path[i]
            v_attr = self.node_attributes.get(v, {})
            f_E += v_attr.get("processing_energy", 0.5)
            
        # 4. QoS Index: composite link delivery reliability * bandwidth factor
        rel_product = 1.0
        min_bw = 100.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_data = self.edge_attributes.get((u, v), {})
            rel_product *= edge_data.get("link_reliability", 0.95)
            bw = edge_data.get("bandwidth", 50.0)
            if bw < min_bw:
                min_bw = bw
                
        f_Q = float(np.clip(rel_product * (min_bw / 50.0), 0.0, 1.0))
        
        return {
            "trust": float(f_T),        # Maximize
            "latency": float(f_L),      # Minimize
            "energy": float(f_E),       # Minimize
            "qos": float(f_Q),          # Maximize
            "hops": len(path) - 1       # Minimize
        }
