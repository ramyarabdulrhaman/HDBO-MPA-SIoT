"""
Mathematical Trust Computation Engine for Social IoT.
Implements Laplace-smoothed direct trust, entropy-weighted indirect recommendation aggregation,
multi-relational Jaccard social proximity, and composite node trust evaluation.
"""

import math
import numpy as np

class TrustEngine:
    def __init__(self, w_d=0.45, w_i=0.35, w_s=0.20, decay_factor=0.95):
        """
        Initializes the Trust Engine.
        w_d: Direct trust weight (default: 0.45)
        w_i: Indirect trust weight (default: 0.35)
        w_s: Social relationship weight (default: 0.20)
        decay_factor: Temporal recency decay lambda_rec
        """
        assert abs((w_d + w_i + w_s) - 1.0) < 1e-6, "Weights must sum to 1.0"
        self.w_d = w_d
        self.w_i = w_i
        self.w_s = w_s
        self.decay_factor = decay_factor

    def compute_direct_trust(self, successes, failures):
        """
        Laplace-smoothed direct trust:
        T_dir = (S + 1) / (S + F + 2)
        """
        return float((successes + 1.0) / (successes + failures + 2.0))

    def compute_recommendation_entropy(self, recommendations, num_bins=5):
        """
        Computes normalized Shannon entropy H in [0, 1] over the recommendation distribution,
        capped properly by log2(min(n, num_bins)) to avoid sample-size distortion.
        """
        if not recommendations:
            return 1.0 # Neutral uncertainty
            
        ratings = list(recommendations.values())
        n = len(ratings)
        if n <= 1:
            return 1.0 # Single rating cannot be penalized for low entropy
            
        # Bin frequencies
        counts, _ = np.histogram(ratings, bins=num_bins, range=(0.0, 1.0))
        probs = [c / n for c in counts if c > 0]
        
        # Max entropy is bounded by min(sample size n, number of bins)
        effective_max = math.log2(min(n, num_bins))
        if effective_max <= 1e-9:
            return 1.0
            
        entropy = -sum(p * math.log2(p) for p in probs)
        norm_entropy = float(entropy / effective_max)
        return float(np.clip(norm_entropy, 0.0, 1.0))

    def compute_indirect_trust(self, requesting_node, target_node, recommendations, 
                               direct_trust_matrix, use_entropy_weighting=True):
        """
        Computes indirect recommendation trust T_ind with robust median/MAD consensus,
        peer direct-trust weighting, and sample-size-calibrated confidence modulation.
        """
        if not recommendations:
            return 0.50 # Neutral fallback
            
        ratings = np.array(list(recommendations.values()), dtype=float)
        recommender_ids = list(recommendations.keys())
        
        if len(ratings) == 1:
            rec_k = recommender_ids[0]
            rel_k = direct_trust_matrix.get((requesting_node, rec_k), 0.5)
            return float(0.50 * 0.50 + 0.50 * (rel_k * ratings[0] + (1.0 - rel_k) * 0.50))

        # Robust consensus: Weighted Median and Median Absolute Deviation (MAD)
        # Prevents honest-minority distortion where colluders skew arithmetic mean
        rec_direct_trusts = np.array([
            direct_trust_matrix.get((requesting_node, k), 0.50) for k in recommender_ids
        ], dtype=float)
        
        # Sort by ratings for weighted median calculation
        sort_idx = np.argsort(ratings)
        sorted_ratings = ratings[sort_idx]
        sorted_weights = rec_direct_trusts[sort_idx]
        cum_weights = np.cumsum(sorted_weights)
        cutoff = cum_weights[-1] / 2.0
        median_idx = np.searchsorted(cum_weights, cutoff)
        median_idx = min(median_idx, len(sorted_ratings) - 1)
        robust_center = float(sorted_ratings[median_idx])
        
        # Median Absolute Deviation (MAD) with 50% theoretical breakdown point
        abs_devs = np.abs(ratings - robust_center)
        mad = float(np.median(abs_devs))
        robust_scale = max(1.4826 * mad, 0.05) # Normal-equivalent scale with minimum floor
        
        if use_entropy_weighting:
            H = self.compute_recommendation_entropy(recommendations)
            weights = []
            for idx, k in enumerate(recommender_ids):
                r_kj = ratings[idx]
                rho_ik = rec_direct_trusts[idx] # Direct trust in recommender
                
                # Robust Gaussian deviation penalty relative to robust median and MAD
                dev_z = (r_kj - robust_center) / robust_scale
                delta = math.exp(-0.5 * (dev_z ** 2))
                
                # Recommender weight fusing peer direct trust and consensus alignment
                q_ik = rho_ik * delta
                weights.append(q_ik)
                
            weights = np.array(weights, dtype=float)
            total_w = np.sum(weights)
            if total_w > 1e-9:
                alpha = weights / total_w
                raw_ind = float(np.sum(alpha * ratings))
                avg_peer_trust = float(np.sum(alpha * rec_direct_trusts))
            else:
                raw_ind = float(robust_center)
                avg_peer_trust = float(np.mean(rec_direct_trusts))
                
            # Calibrated Confidence Gate:
            # If recommenders are highly trusted by requesting node, consensus is trusted even if variance is low.
            # If recommenders have low trust AND zero entropy on extreme values, damp toward neutral prior 0.50.
            conf_gate = np.clip(0.40 + 0.40 * avg_peer_trust + 0.20 * H, 0.0, 1.0)
            t_ind = float(conf_gate * raw_ind + (1.0 - conf_gate) * 0.50)
        else:
            # Unweighted / simple averaging ablation (A3)
            t_ind = float(np.mean(ratings))
            
        return float(np.clip(t_ind, 0.0, 1.0))

    def compute_social_relationship_degree(self, node_i, node_j, graph, edge_attributes):
        """
        Computes social similarity S_rel via multi-relation Jaccard neighborhood similarity:
        S_rel = |N(i) cap N(j)| / |N(i) cup N(j)|
        Augmented with edge relationship strength if a direct link exists.
        Uses internal memoization cache for ultra-fast repeated evaluation.
        """
        if node_i == node_j:
            return 1.0
            
        if not hasattr(self, '_social_cache'):
            self._social_cache = {}
            
        cache_key = (min(node_i, node_j), max(node_i, node_j))
        if cache_key in self._social_cache:
            return self._social_cache[cache_key]
            
        neighbors_i = set(graph.neighbors(node_i)) if node_i in graph else set()
        neighbors_j = set(graph.neighbors(node_j)) if node_j in graph else set()
        
        intersection = neighbors_i.intersection(neighbors_j)
        union = neighbors_i.union(neighbors_j)
        
        jaccard = float(len(intersection) / len(union)) if union else 0.0
        
        # Check direct link relationship weights
        edge_data = edge_attributes.get((node_i, node_j), None)
        if edge_data and "social_relationships" in edge_data:
            rel_weights = {'POR': 0.85, 'C-WOR': 0.75, 'CLOR': 0.65, 'SOR': 0.80, 'OOR': 0.95}
            active_weights = [rel_weights.get(r, 0.5) for r in edge_data["social_relationships"]]
            w_edge = float(np.mean(active_weights)) if active_weights else 0.5
            s_rel = 0.5 * jaccard + 0.5 * w_edge
        else:
            s_rel = jaccard
            
        res = float(np.clip(s_rel, 0.0, 1.0))
        self._social_cache[cache_key] = res
        return res

    def compute_composite_trust(self, t_dir, t_ind, s_rel, 
                                direct_only=False, no_entropy=False, 
                                no_social=False, no_indirect=False):
        """
        Computes composite node trust score:
        T_composite = w_d * T_dir + w_i * T_ind + w_s * S_rel
        Supports ablation configurations.
        """
        if direct_only:
            return float(t_dir)
        elif no_social:
            w_d_prime = self.w_d / (self.w_d + self.w_i)
            w_i_prime = self.w_i / (self.w_d + self.w_i)
            return float(w_d_prime * t_dir + w_i_prime * t_ind)
        elif no_indirect:
            w_d_prime = self.w_d / (self.w_d + self.w_s)
            w_s_prime = self.w_s / (self.w_d + self.w_s)
            return float(w_d_prime * t_dir + w_s_prime * s_rel)
        else:
            return float(self.w_d * t_dir + self.w_i * t_ind + self.w_s * s_rel)

    def evaluate_path_trust(self, path, composite_trust_matrix, tau_min=0.40):
        """
        Evaluates the trust of a service path P = (v_0, v_1, ..., v_k).
        Computes path average trust and applies a smooth, continuous C^1 penalty
        if bottleneck link trust drops below tau_min.
        f_T(P) = 0.75 * avg_T + 0.25 * min_T - 1.5 * max(0, tau_min - min_T)^2
        """
        if len(path) < 2:
            return 1.0
            
        scores = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            score = composite_trust_matrix.get((u, v), 0.5)
            scores.append(score)
            
        avg_trust = float(np.mean(scores))
        min_trust = float(np.min(scores))
        
        # Smooth, continuous, monotonic bottleneck penalty (no jump discontinuity)
        penalty = 1.5 * (max(0.0, tau_min - min_trust) ** 2)
        final_trust = 0.75 * avg_trust + 0.25 * min_trust - penalty
            
        return float(np.clip(final_trust, 0.0, 1.0))

