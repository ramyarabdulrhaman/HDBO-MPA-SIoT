"""
Multi-Objective and Security Evaluation Metrics for Social IoT Service Discovery.
Vectorized implementation of Pareto dominance, Hypervolume (HV), Inverted Generational Distance (IGD+),
Spacing, Trust classification metrics (Precision, Recall, F1, FAR, FRR),
and TOPSIS multi-criteria path selection.
"""

import math
import numpy as np

def dominates(obj_a, obj_b):
    """
    Checks if solution A dominates solution B (A dominates B).
    Objectives: trust (max), latency (min), energy (min), qos (max).
    """
    better_or_equal = (
        obj_a["trust"] >= obj_b["trust"] and
        obj_a["latency"] <= obj_b["latency"] and
        obj_a["energy"] <= obj_b["energy"] and
        obj_a["qos"] >= obj_b["qos"]
    )
    strictly_better = (
        obj_a["trust"] > obj_b["trust"] or
        obj_a["latency"] < obj_b["latency"] or
        obj_a["energy"] < obj_b["energy"] or
        obj_a["qos"] > obj_b["qos"]
    )
    return better_or_equal and strictly_better

def extract_pareto_front(solutions):
    """
    Fast, vectorized extraction of the non-dominated set from a list of solutions.
    """
    if not solutions:
        return []
    if len(solutions) == 1:
        return solutions
        
    # Standardize all to minimization: [-trust, latency, energy, -qos]
    objs = np.array([
        [-s["objectives"]["trust"], s["objectives"]["latency"], s["objectives"]["energy"], -s["objectives"]["qos"]]
        for s in solutions
    ])
    
    N = len(objs)
    is_dominated = np.zeros(N, dtype=bool)
    
    chunk_size = 500
    for start in range(0, N, chunk_size):
        end = min(start + chunk_size, N)
        sub = objs[start:end] # (chunk, 4)
        
        # Check if any j in 0..N dominates i in start..end:
        # objs[j] dominates sub[i] iff all(objs[j] <= sub[i]) and any(objs[j] < sub[i])
        less_equal = objs[None, :, :] <= sub[:, None, :] # (chunk, N, 4)
        strictly_less = objs[None, :, :] < sub[:, None, :] # (chunk, N, 4)
        dom = np.all(less_equal, axis=2) & np.any(strictly_less, axis=2) # (chunk, N)
        
        # Ignore self comparisons
        self_mask = np.arange(N)[None, :] == np.arange(start, end)[:, None]
        dom[self_mask] = False
        is_dominated[start:end] = np.any(dom, axis=1)
        
    filtered = []
    seen = set()
    for idx in np.where(~is_dominated)[0]:
        sol = solutions[idx]
        key = (
            round(sol["objectives"]["trust"], 4),
            round(sol["objectives"]["latency"], 1),
            round(sol["objectives"]["energy"], 2),
            round(sol["objectives"]["qos"], 4)
        )
        if key not in seen:
            seen.add(key)
            filtered.append(sol)
            
    return filtered

def normalize_objectives(objectives, bounds):
    lat_min, lat_max = bounds.get("latency", (5.0, 120.0))
    eng_min, eng_max = bounds.get("energy", (0.5, 15.0))
    
    n_trust = float(np.clip(objectives["trust"], 0.0, 1.0))
    n_lat = float(np.clip(1.0 - (objectives["latency"] - lat_min) / (lat_max - lat_min + 1e-6), 0.0, 1.0))
    n_eng = float(np.clip(1.0 - (objectives["energy"] - eng_min) / (eng_max - eng_min + 1e-6), 0.0, 1.0))
    n_qos = float(np.clip(objectives["qos"], 0.0, 1.0))
    
    return np.array([n_trust, n_lat, n_eng, n_qos])

def compute_hypervolume(solutions, bounds=None, num_samples=1000, seed=42):
    """
    Fast, vectorized Monte Carlo Hypervolume calculation in [0, 1]^4.
    """
    if not solutions:
        return 0.0
    if bounds is None:
        bounds = {"latency": (5.0, 120.0), "energy": (0.5, 15.0)}
        
    norm_points = np.array([normalize_objectives(sol["objectives"], bounds) for sol in solutions]) # (K, 4)
    rng = np.random.RandomState(seed)
    samples = rng.uniform(0.0, 1.0, size=(num_samples, 4)) # (S, 4)
    
    # Vectorized check: sample is dominated if any norm_point dominates it (norm_point >= sample)
    all_dims = np.all(samples[:, None, :] <= norm_points[None, :, :], axis=2) # (S, K)
    dominated = np.any(all_dims, axis=1) # (S,)
    return float(np.mean(dominated))

def compute_igd_plus(solutions, reference_front, bounds=None):
    if not solutions or not reference_front:
        return 1.0
    if bounds is None:
        bounds = {"latency": (5.0, 120.0), "energy": (0.5, 15.0)}
        
    A = np.array([normalize_objectives(sol["objectives"], bounds) for sol in solutions]) # (M, 4)
    R = np.array([normalize_objectives(sol["objectives"], bounds) for sol in reference_front]) # (N, 4)
    
    # Vectorized modified distance: d+(a, r) = sqrt(sum(max(r - a, 0)^2))
    diff = np.maximum(R[:, None, :] - A[None, :, :], 0.0) # (N, M, 4)
    d_plus = np.sqrt(np.sum(diff**2, axis=2)) # (N, M)
    min_dists = np.min(d_plus, axis=1) # (N,)
    return float(np.mean(min_dists))

def compute_spacing(solutions, bounds=None):
    if len(solutions) < 2:
        return 0.0
    if bounds is None:
        bounds = {"latency": (5.0, 120.0), "energy": (0.5, 15.0)}
        
    pts = np.array([normalize_objectives(sol["objectives"], bounds) for sol in solutions])
    
    # Pairwise Manhattan distances
    diff = np.abs(pts[:, None, :] - pts[None, :, :])
    manhattan = np.sum(diff, axis=2)
    np.fill_diagonal(manhattan, np.inf)
    min_dists = np.min(manhattan, axis=1)
    
    d_mean = np.mean(min_dists)
    s = np.sqrt(np.sum((min_dists - d_mean)**2) / (len(pts) - 1))
    return float(s)

def topsis_selection(solutions, weights=(0.35, 0.25, 0.25, 0.15), bounds=None):
    if not solutions:
        return None
    if len(solutions) == 1:
        return solutions[0]
    if bounds is None:
        bounds = {"latency": (5.0, 120.0), "energy": (0.5, 15.0)}
        
    matrix = np.array([normalize_objectives(sol["objectives"], bounds) for sol in solutions])
    ideal_best = np.ones(4)
    ideal_worst = np.zeros(4)
    w = np.array(weights) / np.sum(weights)
    
    d_best = np.sqrt(np.sum(w * (matrix - ideal_best)**2, axis=1))
    d_worst = np.sqrt(np.sum(w * (matrix - ideal_worst)**2, axis=1))
    scores = d_worst / (d_best + d_worst + 1e-9)
    best_idx = int(np.argmax(scores))
    return solutions[best_idx]

def compute_trust_classification_metrics(node_attributes, composite_trust_scores, threshold=0.55):
    """
    Computes rigorous ground-truth classification metrics for malicious node detection:
    - Positive: Malicious node (Actual P = TP + FN)
    - Negative: Honest node (Actual N = TN + FP)
    - True Positive (TP): Malicious node correctly detected as malicious (score < threshold)
    - False Positive (FP): Honest node incorrectly flagged as malicious (score < threshold)
    - True Negative (TN): Honest node correctly admitted as honest (score >= threshold)
    - False Negative (FN): Malicious node erroneously accepted as honest (score >= threshold)
    
    Metrics:
    - Precision = TP / (TP + FP)
    - Recall / TPR = TP / (TP + FN)
    - FAR (False Acceptance Rate / FNR) = FN / (FN + TP) [Rate of accepting malicious nodes]
    - FRR (False Rejection Rate / FPR) = FP / (FP + TN) [Rate of rejecting honest nodes]
    - F1-Score = 2 * Precision * Recall / (Precision + Recall)
    """
    tp, fp, tn, fn = 0, 0, 0, 0
    for node_id, attr in node_attributes.items():
        is_mal = attr.get("is_malicious", False)
        score = composite_trust_scores.get(node_id, 0.50)
        predicted_mal = (score < threshold)
        
        if is_mal and predicted_mal:
            tp += 1
        elif not is_mal and predicted_mal:
            fp += 1
        elif not is_mal and not predicted_mal:
            tn += 1
        else:
            fn += 1
            
    actual_pos = tp + fn
    actual_neg = tn + fp
    pred_pos = tp + fp
    
    precision = tp / pred_pos if pred_pos > 0 else 0.0
    recall = tp / actual_pos if actual_pos > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Standard security definitions:
    far = fn / actual_pos if actual_pos > 0 else 0.0  # False Acceptance of malicious nodes
    frr = fp / actual_neg if actual_neg > 0 else 0.0  # False Rejection of honest nodes
    
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": float(precision),
        "recall": float(recall),
        "tpr": float(recall),
        "fpr": float(frr),
        "f1": float(f1),
        "far": float(far),
        "frr": float(frr)
    }

def compute_path_security_metrics(path, node_attributes):
    """
    Computes ground-truth security performance along an end-to-end service path:
    - Malicious node count and fraction along path
    - True delivery success (whether the path avoids packet droppers or compromised relays)
    """
    if not path:
        return {"malicious_count": 0, "malicious_fraction": 0.0, "is_compromised": False, "delivery_success": False}
        
    intermediate_and_dest = path[1:] # Exclude source requester
    mal_count = sum(1 for n in intermediate_and_dest if node_attributes.get(n, {}).get("is_malicious", False))
    mal_frac = float(mal_count / len(intermediate_and_dest)) if intermediate_and_dest else 0.0
    is_compromised = (mal_count > 0)
    
    # Path delivery succeeds if no intermediate or destination node actively drops service
    delivery_success = True
    for n in intermediate_and_dest:
        attr = node_attributes.get(n, {})
        if attr.get("is_malicious", False):
            atk = attr.get("attack_type", "none")
            if atk in ["service_drop", "on_off", "collusion"]:
                delivery_success = False
                break
                
    return {
        "malicious_count": mal_count,
        "malicious_fraction": mal_frac,
        "is_compromised": is_compromised,
        "delivery_success": delivery_success
    }

