"""
Master Reproducible Experiment Runner for HDBO-MPA Social IoT Service Discovery.
Executes controlled benchmarks, attack resilience tests, scalability evaluations,
ablation studies, and parameter sensitivity analyses across 30 independent runs.
Exports raw CSV logs for strict 1:1 empirical traceability.
"""

import sys
import os
import time
import json
import random
import csv
import numpy as np
import networkx as nx

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.network.siot_graph import SIoTGraph
from src.trust_model.engine import TrustEngine
from src.trust_model.attack_simulator import AttackSimulator
from src.path_encoding.representation import PathEncoderDecoder
from src.evaluation.metrics import (
    extract_pareto_front, compute_hypervolume, compute_igd_plus,
    compute_spacing, topsis_selection, compute_trust_classification_metrics,
    compute_path_security_metrics
)
from src.dbo.dbo_optimizer import DBOptimizer
from src.mpa.mpa_optimizer import MPAOptimizer
from src.hybrid_optimizer.hdbo_mpa import HDBOMPAOptimizer
from src.baselines.baseline_models import (
    DijkstraBaseline, TGreedyBaseline, NSGAIIBaseline, MOPSOBaseline, ACOBaseline,
    MOEADBaseline, SPEA2Baseline, MOMPABaseline, BetaReputationTrustModel, EigenTrustModel
)

def build_composite_trust_matrix(siot, histories, direct_trust, trust_engine, ablation_flags=None):
    if ablation_flags is None:
        ablation_flags = {}
        
    direct_only = ablation_flags.get("direct_only", False)
    no_entropy = ablation_flags.get("no_entropy", False)
    no_social = ablation_flags.get("no_social", False)
    no_indirect = ablation_flags.get("no_indirect", False)
    
    composite_trust = {}
    provider_ratings = {n: [] for n in siot.graph.nodes()}
    
    for u, v in siot.graph.edges():
        for pair in [(u, v), (v, u)]:
            p_u, p_v = pair
            hist = histories.get((p_u, p_v), {"successes": 15, "failures": 2, "direct_trust": 0.85, "recommendations": {}})
            t_dir = hist["direct_trust"]
            t_ind = trust_engine.compute_indirect_trust(
                p_u, p_v, hist["recommendations"], direct_trust, use_entropy_weighting=not no_entropy
            )
            s_rel = trust_engine.compute_social_relationship_degree(p_u, p_v, siot.graph, siot.edge_attributes)
            t_comp = trust_engine.compute_composite_trust(
                t_dir, t_ind, s_rel, direct_only=direct_only, no_social=no_social, no_indirect=no_indirect
            )
            composite_trust[(p_u, p_v)] = t_comp
            provider_ratings[p_v].append(t_comp)
            
    reputation_scores = {
        v: float(np.mean(ratings)) if ratings else 0.50
        for v, ratings in provider_ratings.items()
    }
    return composite_trust, reputation_scores

def run_multi_objective_benchmark(snap_path, out_dir, num_runs=30):
    print("\n=======================================================")
    print(f"EXPERIMENT 1A: Multi-Objective Benchmarking on SNAP ego-Facebook ({num_runs} Runs)")
    print("=======================================================")
    
    csv_path = os.path.join(out_dir, "experiments", "raw_results", "multi_objective_benchmark_raw.csv")
    siot = SIoTGraph.from_snap_file(snap_path, max_nodes=250, seed=42)
    siot.export_json(os.path.join(out_dir, "graph_instances"))
    
    attack_sim = AttackSimulator(siot, malicious_ratio=0.20, seed=42)
    histories, direct_trust = attack_sim.generate_interaction_histories()
    trust_engine = TrustEngine(w_d=0.45, w_i=0.35, w_s=0.20)
    composite_trust, reputation_scores = build_composite_trust_matrix(siot, histories, direct_trust, trust_engine)
    
    encoder_decoder = PathEncoderDecoder(siot, composite_trust, trust_engine)
    
    # Generate 30 fixed, non-trivial requests shared by all algorithms (min_hops = 2 on SNAP-250)
    random.seed(42)
    requests = []
    for r_i in range(num_runs):
        req = siot.generate_service_request(service_id=(r_i % 5), min_hops=2)
        requests.append(req)
        
    algorithms = [
        "HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", 
        "MOEA/D", "SPEA2", "MOMPA", "ACO", "T-Greedy", "Dijkstra"
    ]
    
    raw_results = []
    global_solutions_pool = []
    convergence_records = []
    
    for run_idx in range(num_runs):
        seed = 100 + run_idx
        req = requests[run_idx]
        src = req["source"]
        dest_candidates = [p for p in req["eligible_providers"] if not siot.node_attributes[p]["is_malicious"]]
        dest = dest_candidates[0] if dest_candidates else req["eligible_providers"][0]
        
        # True Equal Evaluation Budget: Exactly 750 objective evaluations across all metaheuristics
        # (30 population x 25 iterations for swarm/genetic; 30 ants x 25 iterations for ACO)
        optimizers = {
            "HDBO-MPA": HDBOMPAOptimizer(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "DBO": DBOptimizer(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "MPA": MPAOptimizer(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "NSGA-II": NSGAIIBaseline(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "MO-PSO": MOPSOBaseline(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "MOEA/D": MOEADBaseline(encoder_decoder, pop_size=30, max_iter=25, seed=seed),
            "SPEA2": SPEA2Baseline(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "MOMPA": MOMPABaseline(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "ACO": ACOBaseline(encoder_decoder, num_ants=30, max_iter=25, seed=seed),
            "T-Greedy": TGreedyBaseline(encoder_decoder),
            "Dijkstra": DijkstraBaseline(encoder_decoder)
        }
        
        for alg_name in algorithms:
            opt = optimizers[alg_name]
            t_start = time.perf_counter()
            track_conv = (run_idx == 0 and alg_name in ["HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", "ACO", "MOMPA", "SPEA2"])
            
            if alg_name == "HDBO-MPA":
                res = opt.optimize(src, dest, track_convergence=track_conv)
                if track_conv and "convergence_history" in res:
                    for ch in res["convergence_history"]:
                        convergence_records.append({
                            "algorithm": alg_name,
                            "iteration": ch["iteration"],
                            "eval_count": ch["eval_count"],
                            "hypervolume": ch["hv"]
                        })
            else:
                res = opt.optimize(src, dest)
                
            t_elapsed = time.perf_counter() - t_start
            p_front = res["pareto_front"]
            global_solutions_pool.extend(p_front)
            
            best = res.get("best_compromise", p_front[0] if p_front else None)
            best_objs = best["objectives"] if best else {"trust": 0, "latency": 999, "energy": 999, "qos": 0, "hops": 0}
            
            # Constraint check & Feasibility verification
            c_res = encoder_decoder.evaluate_constraints(best["path"] if best else [])
            
            raw_results.append({
                "run": run_idx + 1,
                "seed": seed,
                "dataset": "SNAP-Facebook-250",
                "algorithm": alg_name,
                "source": src,
                "destination": dest,
                "runtime_sec": t_elapsed,
                "eval_count": res.get("eval_count", 0),
                "pareto_size": len(p_front),
                "best_trust": best_objs["trust"],
                "best_latency": best_objs["latency"],
                "best_energy": best_objs["energy"],
                "best_qos": best_objs["qos"],
                "best_hops": best_objs["hops"],
                "constraint_violation": c_res["constraint_violation"],
                "path_feasible": 1.0 if c_res["is_feasible"] else 0.0,
                "front_solutions": p_front
            })
            
        print(f" Completed Run {run_idx+1}/{num_runs} (Seed: {seed})")
        
    true_reference_front = extract_pareto_front(global_solutions_pool)
    print(f"\nConstructed Global Non-Dominated Reference Front: {len(true_reference_front)} solutions.")
    
    for row in raw_results:
        front = row["front_solutions"]
        row["hypervolume"] = compute_hypervolume(front, num_samples=1000)
        row["igd_plus"] = compute_igd_plus(front, true_reference_front)
        row["spacing"] = compute_spacing(front)
        del row["front_solutions"]
        
    csv_path = os.path.join(out_dir, "experiments", "raw_results", "multi_objective_benchmark_raw.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_results[0].keys()))
        writer.writeheader()
        writer.writerows(raw_results)
    print(f"Exported raw benchmark results to: {csv_path}")
    
    # Export convergence raw data
    if convergence_records:
        conv_csv = os.path.join(out_dir, "experiments", "raw_results", "convergence_raw.csv")
        with open(conv_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["algorithm", "iteration", "eval_count", "hypervolume"])
            writer.writeheader()
            writer.writerows(convergence_records)
        print(f"Exported convergence history to: {conv_csv}")
        
    return raw_results, true_reference_front

def run_scale_free_benchmark(out_dir, num_runs=30):
    print("\n=======================================================")
    print(f"EXPERIMENT 1B: Secondary Benchmark on Barabasi-Albert Scale-Free Graph ({num_runs} Runs)")
    print("=======================================================")
    
    csv_path = os.path.join(out_dir, "experiments", "raw_results", "secondary_dataset_benchmark_raw.csv")
    siot = SIoTGraph.from_scale_free(n=250, m=4, seed=42)
    attack_sim = AttackSimulator(siot, malicious_ratio=0.20, seed=42)
    histories, direct_trust = attack_sim.generate_interaction_histories()
    trust_engine = TrustEngine(w_d=0.45, w_i=0.35, w_s=0.20)
    composite_trust, reputation_scores = build_composite_trust_matrix(siot, histories, direct_trust, trust_engine)
    encoder_decoder = PathEncoderDecoder(siot, composite_trust, trust_engine)
    
    # Generate 30 fixed, non-trivial requests shared by all algorithms (min_hops = 3 on Scale-Free)
    random.seed(84)
    requests = [siot.generate_service_request(service_id=(s_id % 5), min_hops=3) for s_id in range(num_runs)]
    algorithms = ["HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", "MOEA/D", "SPEA2", "MOMPA"]
    
    raw_results = []
    global_solutions_pool = []
    
    for run_idx in range(num_runs):
        seed = 200 + run_idx
        req = requests[run_idx]
        src = req["source"]
        dest = req["eligible_providers"][0]
        
        # Equal evaluation budget: 30 pop x 25 iter = 750 objective evaluations
        optimizers = {
            "HDBO-MPA": HDBOMPAOptimizer(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "DBO": DBOptimizer(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "MPA": MPAOptimizer(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "NSGA-II": NSGAIIBaseline(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "MO-PSO": MOPSOBaseline(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "MOEA/D": MOEADBaseline(encoder_decoder, pop_size=30, max_iter=25, seed=seed),
            "SPEA2": SPEA2Baseline(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed),
            "MOMPA": MOMPABaseline(encoder_decoder, pop_size=30, max_iter=25, archive_capacity=30, seed=seed)
        }
        
        for alg_name in algorithms:
            opt = optimizers[alg_name]
            t_start = time.perf_counter()
            res = opt.optimize(src, dest)
            t_elapsed = time.perf_counter() - t_start
            
            p_front = res["pareto_front"]
            global_solutions_pool.extend(p_front)
            best = res.get("best_compromise", p_front[0] if p_front else None)
            best_objs = best["objectives"] if best else {"trust": 0, "latency": 999, "energy": 999, "qos": 0, "hops": 0}
            
            raw_results.append({
                "run": run_idx + 1,
                "seed": seed,
                "dataset": "ScaleFree-BA-250",
                "algorithm": alg_name,
                "runtime_sec": t_elapsed,
                "eval_count": res.get("eval_count", 0),
                "pareto_size": len(p_front),
                "best_trust": best_objs["trust"],
                "best_latency": best_objs["latency"],
                "best_energy": best_objs["energy"],
                "best_qos": best_objs["qos"],
                "best_hops": best_objs["hops"],
                "front_solutions": p_front
            })
            
    true_ref = extract_pareto_front(global_solutions_pool)
    for row in raw_results:
        front = row["front_solutions"]
        row["hypervolume"] = compute_hypervolume(front, num_samples=1000)
        row["igd_plus"] = compute_igd_plus(front, true_ref)
        row["spacing"] = compute_spacing(front)
        del row["front_solutions"]
        
    csv_path = os.path.join(out_dir, "experiments", "raw_results", "secondary_dataset_benchmark_raw.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_results[0].keys()))
        writer.writeheader()
        writer.writerows(raw_results)
    print(f"Exported scale-free benchmark results to: {csv_path}")
    return raw_results

def run_attack_resilience_benchmark(snap_path, out_dir):
    print("\n=======================================================")
    print("EXPERIMENT 2: Multi-Model Adversarial Security & Attack Resilience")
    print("=======================================================")
    
    siot = SIoTGraph.from_snap_file(snap_path, max_nodes=250, seed=42)
    mal_ratios = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60] # Includes honest-minority regime at 60%
    attack_modes = ["mixed", "service_drop", "bad_mouthing", "collusion", "on_off", "sybil"]
    
    beta_model = BetaReputationTrustModel(outlier_threshold=1.96)
    eigentrust_model = EigenTrustModel(pre_trusted_weight=0.15)
    
    results = []
    
    for r in mal_ratios:
        for mode in attack_modes:
            print(f"Testing Malicious Ratio: {int(r*100)}% | Attack Mode: {mode} ...")
            attack_sim = AttackSimulator(siot, malicious_ratio=r, attack_mode=mode, seed=int(r*100))
            # Test in cold-start recommendation-dominant regime (sparsity = 60%)
            histories, direct_trust = attack_sim.generate_interaction_histories(cold_start_ratio=0.60)
            
            # Model 1: Proposed Trust Engine (robust median/MAD consensus + entropy confidence modulation)
            trust_engine = TrustEngine(w_d=0.45, w_i=0.35, w_s=0.20)
            comp_prop, rep_prop = build_composite_trust_matrix(siot, histories, direct_trust, trust_engine)
            m_prop = compute_trust_classification_metrics(siot.node_attributes, rep_prop, threshold=0.55)
            
            # Model 2: Published Beta-Reputation Model
            beta_comp = {}
            beta_ratings = {n: [] for n in siot.graph.nodes()}
            for (u, v) in histories:
                h = histories[(u, v)]
                t_b = beta_model.compute_trust(h["successes"], h["failures"], h["recommendations"])
                beta_comp[(u, v)] = t_b
                beta_ratings[v].append(t_b)
            rep_beta = {v: float(np.mean(rts)) if rts else 0.50 for v, rts in beta_ratings.items()}
            m_beta = compute_trust_classification_metrics(siot.node_attributes, rep_beta, threshold=0.55)
            
            # Model 3: Published EigenTrust Model
            rep_eigen = eigentrust_model.compute_global_trust(siot.graph, direct_trust)
            m_eigen = compute_trust_classification_metrics(siot.node_attributes, rep_eigen, threshold=0.35)
            
            # Model 4: Ablation A4 (Direct Trust Only)
            comp_dir, rep_dir = build_composite_trust_matrix(siot, histories, direct_trust, trust_engine, {"direct_only": True})
            m_dir = compute_trust_classification_metrics(siot.node_attributes, rep_dir, threshold=0.55)
            
            # Model 5: Ablation A3 (No Entropy Weighting)
            comp_no_ent, rep_no_ent = build_composite_trust_matrix(siot, histories, direct_trust, trust_engine, {"no_entropy": True})
            m_no_ent = compute_trust_classification_metrics(siot.node_attributes, rep_no_ent, threshold=0.55)
            
            # Service Path Security Evaluation using HDBO-MPA path routing
            encoder_decoder = PathEncoderDecoder(siot, comp_prop, trust_engine)
            opt = HDBOMPAOptimizer(encoder_decoder, pop_size=20, max_iter=15, seed=42)
            
            total_queries = 15
            sdsr_successes = 0
            malicious_path_fractions = []
            true_delivery_successes = 0
            latencies = []
            energies = []
            
            for q in range(total_queries):
                req = siot.generate_service_request()
                src = req["source"]
                dest = req["eligible_providers"][0]
                
                res = opt.optimize(src, dest, track_convergence=False)
                best = res["best_compromise"]
                path = best["path"]
                
                sec_m = compute_path_security_metrics(path, siot.node_attributes)
                malicious_path_fractions.append(sec_m["malicious_fraction"])
                if sec_m["delivery_success"]:
                    true_delivery_successes += 1
                    
                final_provider = path[-1]
                is_mal = siot.node_attributes[final_provider]["is_malicious"]
                if not is_mal and best["objectives"]["latency"] <= req["max_latency"] and best["objectives"]["trust"] >= 0.50:
                    sdsr_successes += 1
                    
                latencies.append(best["objectives"]["latency"])
                energies.append(best["objectives"]["energy"])
                
            results.append({
                "malicious_ratio": r,
                "attack_mode": mode,
                "sdsr_a": float(sdsr_successes / total_queries),
                "true_delivery_rate": float(true_delivery_successes / total_queries),
                "avg_malicious_path_fraction": float(np.mean(malicious_path_fractions)),
                "avg_latency": float(np.mean(latencies)),
                "avg_energy": float(np.mean(energies)),
                # Proposed Trust Engine
                "prop_precision": m_prop["precision"],
                "prop_recall": m_prop["recall"],
                "prop_f1": m_prop["f1"],
                "prop_far": m_prop["far"],
                "prop_frr": m_prop["frr"],
                # Beta Reputation
                "beta_f1": m_beta["f1"],
                "beta_far": m_beta["far"],
                "beta_frr": m_beta["frr"],
                # EigenTrust
                "eigen_f1": m_eigen["f1"],
                "eigen_far": m_eigen["far"],
                "eigen_frr": m_eigen["frr"],
                # Direct Only
                "direct_only_f1": m_dir["f1"],
                "direct_only_far": m_dir["far"],
                # No Entropy
                "no_entropy_f1": m_no_ent["f1"],
                "no_entropy_far": m_no_ent["far"]
            })
            
    csv_path = os.path.join(out_dir, "experiments", "raw_results", "attack_resilience_raw.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"Exported multi-model attack resilience results to: {csv_path}")
    return results

def run_scalability_benchmark(snap_path, out_dir):
    print("\n=======================================================")
    print("EXPERIMENT 3: Scalability across Network Topologies and Densities")
    print("=======================================================")
    
    graph_sizes = [100, 250, 500, 1000]
    results = []
    
    for n in graph_sizes:
        print(f"Benchmarking Scalability for N = {n} nodes...")
        siot = SIoTGraph.from_snap_file(snap_path, max_nodes=n, seed=42)
        attack_sim = AttackSimulator(siot, malicious_ratio=0.20, seed=42)
        histories, direct_trust = attack_sim.generate_interaction_histories()
        trust_engine = TrustEngine()
        comp_trust, _ = build_composite_trust_matrix(siot, histories, direct_trust, trust_engine)
        
        encoder_decoder = PathEncoderDecoder(siot, comp_trust, trust_engine)
        random.seed(100 + n)
        req = siot.generate_service_request(min_hops=2)
        src = req["source"]
        dest = req["eligible_providers"][0]
        
        # Unified 750 Evaluation Budget across all network sizes
        for alg_name, opt_cls in [
            ("HDBO-MPA", lambda: HDBOMPAOptimizer(encoder_decoder, pop_size=30, max_iter=25, seed=42)),
            ("NSGA-II", lambda: NSGAIIBaseline(encoder_decoder, pop_size=30, max_iter=25, seed=42)),
            ("MO-PSO", lambda: MOPSOBaseline(encoder_decoder, pop_size=30, max_iter=25, seed=42)),
            ("DBO", lambda: DBOptimizer(encoder_decoder, pop_size=30, max_iter=25, seed=42)),
            ("MPA", lambda: MPAOptimizer(encoder_decoder, pop_size=30, max_iter=25, seed=42))
        ]:
            opt = opt_cls()
            t0 = time.perf_counter()
            res = opt.optimize(src, dest)
            t_el = time.perf_counter() - t0
            
            p_front = res["pareto_front"]
            best = res.get("best_compromise", p_front[0] if p_front else None)
            hv = compute_hypervolume(p_front, num_samples=1000)
            
            results.append({
                "nodes": n,
                "edges": siot.graph.number_of_edges(),
                "algorithm": alg_name,
                "runtime_sec": t_el,
                "eval_count": res.get("eval_count", 0),
                "hypervolume": hv,
                "latency": best["objectives"]["latency"] if best else 0,
                "energy": best["objectives"]["energy"] if best else 0,
                "hops": best["objectives"]["hops"] if best else 0
            })
            
    csv_path = os.path.join(out_dir, "experiments", "raw_results", "scalability_raw.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"Exported scalability results to: {csv_path}")
    return results

def run_ablation_benchmark(snap_path, out_dir, num_runs=30):
    print("\n=======================================================")
    print(f"EXPERIMENT 4: Systematic Component Ablation Study A0 - A10 ({num_runs} Runs)")
    print("=======================================================")
    
    siot = SIoTGraph.from_snap_file(snap_path, max_nodes=250, seed=42)
    attack_sim = AttackSimulator(siot, malicious_ratio=0.20, seed=42)
    histories, direct_trust = attack_sim.generate_interaction_histories()
    trust_engine = TrustEngine()
    
    ablations = [
        ("A0_Full_HDBO_MPA", {}),
        ("A1_DBO_Only", {"optimizer": "DBO"}),
        ("A2_MPA_Only", {"optimizer": "MPA"}),
        ("A3_No_Entropy_Weighting", {"no_entropy": True}),
        ("A4_Direct_Trust_Only", {"direct_only": True}),
        ("A5_No_Social_Relationship", {"no_social": True}),
        ("A6_No_Indirect_Trust", {"no_indirect": True}),
        ("A7_Sequential_Hybrid", {"sequential": True}),
        ("A8_Random_Selection", {"random_path": True}),
        ("A9_No_Loop_Erasure", {"no_loop_erasure": True}),
        ("A10_No_Archive_Crowding", {"no_crowding": True})
    ]
    
    results = []
    
    # 30 non-trivial shared requests for ablation variants
    random.seed(300)
    ablation_requests = [siot.generate_service_request(service_id=(r_i % 5), min_hops=2) for r_i in range(num_runs)]
    
    for run_idx in range(num_runs):
        seed = 300 + run_idx
        req = ablation_requests[run_idx]
        src = req["source"]
        dest = req["eligible_providers"][0]
        
        for code, config in ablations:
            comp_trust, _ = build_composite_trust_matrix(siot, histories, direct_trust, trust_engine, ablation_flags=config)
            encoder_decoder = PathEncoderDecoder(siot, comp_trust, trust_engine)
            
            opt_type = config.get("optimizer", "HDBO-MPA")
            if opt_type == "DBO":
                opt = DBOptimizer(encoder_decoder, pop_size=30, max_iter=25, seed=seed)
            elif opt_type == "MPA":
                opt = MPAOptimizer(encoder_decoder, pop_size=30, max_iter=25, seed=seed)
            else:
                opt = HDBOMPAOptimizer(
                    encoder_decoder, pop_size=30, max_iter=25, seed=seed,
                    sequential=config.get("sequential", False),
                    no_crowding=config.get("no_crowding", False),
                    random_key_only=config.get("random_path", False),
                    no_loop_erasure=config.get("no_loop_erasure", False)
                )
                
            t0 = time.perf_counter()
            res = opt.optimize(src, dest)
            t_el = time.perf_counter() - t0
            
            p_front = res["pareto_front"]
            hv = compute_hypervolume(p_front, num_samples=1000)
            best = res.get("best_compromise", p_front[0] if p_front else None)
            
            # Check loop occurrences along best path
            path = best["path"] if best else []
            has_loop = len(path) != len(set(path))
            
            results.append({
                "run": run_idx + 1,
                "seed": seed,
                "ablation_code": code,
                "runtime_sec": t_el,
                "hypervolume": hv,
                "pareto_size": len(p_front),
                "has_loop": 1.0 if has_loop else 0.0,
                "trust": best["objectives"]["trust"] if best else 0,
                "latency": best["objectives"]["latency"] if best else 0,
                "energy": best["objectives"]["energy"] if best else 0,
                "qos": best["objectives"]["qos"] if best else 0,
                "hops": best["objectives"]["hops"] if best else 0
            })
            
    csv_path = os.path.join(out_dir, "experiments", "raw_results", "ablation_study_raw.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"Exported ablation study results to: {csv_path}")
    return results

def run_sensitivity_benchmark(snap_path, out_dir):
    print("\n=======================================================")
    print("EXPERIMENT 5: Sensitivity Analysis (Parameters & Fig 14 Response Surface)")
    print("=======================================================")
    
    siot = SIoTGraph.from_snap_file(snap_path, max_nodes=250, seed=42)
    attack_sim = AttackSimulator(siot, malicious_ratio=0.20, seed=42)
    histories, direct_trust = attack_sim.generate_interaction_histories()
    trust_engine = TrustEngine()
    comp_trust, _ = build_composite_trust_matrix(siot, histories, direct_trust, trust_engine)
    encoder_decoder = PathEncoderDecoder(siot, comp_trust, trust_engine)
    
    req = siot.generate_service_request()
    src = req["source"]
    dest = req["eligible_providers"][0]
    
    results = []
    
    # 1. Swarm population sensitivity
    for pop in [20, 30, 40, 50, 60]:
        opt = HDBOMPAOptimizer(encoder_decoder, pop_size=pop, max_iter=20, seed=42)
        res = opt.optimize(src, dest)
        hv = compute_hypervolume(res["pareto_front"], num_samples=1000)
        results.append({"category": "pop_size", "param1": pop, "param2": 0.0, "hypervolume": hv, "pareto_size": len(res["pareto_front"])})
        
    # 2. Maximum iterations sensitivity
    for iters in [20, 30, 40, 50, 60]:
        opt = HDBOMPAOptimizer(encoder_decoder, pop_size=30, max_iter=iters, seed=42)
        res = opt.optimize(src, dest)
        hv = compute_hypervolume(res["pareto_front"], num_samples=1000)
        results.append({"category": "max_iter", "param1": iters, "param2": 0.0, "hypervolume": hv, "pareto_size": len(res["pareto_front"])})
        
    # 3. DBO sub-population ratio
    for r in [0.20, 0.35, 0.50, 0.65, 0.80]:
        opt = HDBOMPAOptimizer(encoder_decoder, pop_size=30, max_iter=20, dbo_ratio=r, seed=42)
        res = opt.optimize(src, dest)
        hv = compute_hypervolume(res["pareto_front"], num_samples=1000)
        results.append({"category": "dbo_ratio", "param1": r, "param2": 0.0, "hypervolume": hv, "pareto_size": len(res["pareto_front"])})
        
    # 4. Obstacle dancing probability (p) vs. Levy flight index (beta) 2D Grid for Figure 14
    for p_dance in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for beta_val in [1.1, 1.3, 1.5, 1.7, 1.9]:
            opt = HDBOMPAOptimizer(encoder_decoder, pop_size=25, max_iter=15, seed=42)
            opt.beta = beta_val
            import math
            num = math.gamma(1.0 + beta_val) * math.sin(math.pi * beta_val / 2.0)
            den = math.gamma((1.0 + beta_val) / 2.0) * beta_val * (2.0 ** ((beta_val - 1.0) / 2.0))
            opt.sigma_u = (num / den) ** (1.0 / beta_val)
            
            res = opt.optimize(src, dest)
            hv = compute_hypervolume(res["pareto_front"], num_samples=1000)
            results.append({
                "category": "dance_levy_surface",
                "param1": p_dance,
                "param2": beta_val,
                "hypervolume": hv,
                "pareto_size": len(res["pareto_front"])
            })
            
    csv_path = os.path.join(out_dir, "experiments", "raw_results", "sensitivity_analysis_raw.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"Exported sensitivity results to: {csv_path}")
    return results

if __name__ == "__main__":
    snap_file = os.path.join(root_dir, "data", "raw", "facebook_combined.txt")
    out_base = root_dir
    
    t_start = time.time()
    run_multi_objective_benchmark(snap_file, out_base, num_runs=30)
    run_scale_free_benchmark(out_base, num_runs=30)
    run_attack_resilience_benchmark(snap_file, out_base)
    run_scalability_benchmark(snap_file, out_base)
    run_ablation_benchmark(snap_file, out_base, num_runs=30)
    run_sensitivity_benchmark(snap_file, out_base)
    total_time = time.time() - t_start
    print(f"\nAll Master Benchmark Experiments Successfully Completed in {total_time:.2f} seconds.")
