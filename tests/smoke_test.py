"""
Smoke Test to verify end-to-end functionality of all modules in HDBO_MPA_SIoT_Research.
"""

import sys
import os

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.network.siot_graph import SIoTGraph
from src.trust_model.engine import TrustEngine
from src.trust_model.attack_simulator import AttackSimulator
from src.path_encoding.representation import PathEncoderDecoder
from src.evaluation.metrics import compute_hypervolume, compute_trust_classification_metrics
from src.dbo.dbo_optimizer import DBOptimizer
from src.mpa.mpa_optimizer import MPAOptimizer
from src.hybrid_optimizer.hdbo_mpa import HDBOMPAOptimizer
from src.baselines.baseline_models import DijkstraBaseline, TGreedyBaseline, NSGAIIBaseline, MOPSOBaseline, ACOBaseline

def run_smoke_test():
    print("=== Starting Smoke Test ===")
    snap_txt = os.path.join(root_dir, "data", "raw", "facebook_combined.txt")
    assert os.path.exists(snap_txt), f"SNAP data file missing at {snap_txt}"
    
    print("1. Loading SIoT graph instance (N=50 for quick test)...")
    siot = SIoTGraph.from_snap_file(snap_txt, max_nodes=50, seed=123)
    print(f"   Nodes: {siot.graph.number_of_nodes()}, Edges: {siot.graph.number_of_edges()}")
    
    print("2. Simulating attacks and generating trust histories...")
    attack_sim = AttackSimulator(siot, malicious_ratio=0.20, seed=123)
    histories, direct_trust = attack_sim.generate_interaction_histories()
    print(f"   Malicious nodes: {len(attack_sim.malicious_nodes)}, Honest: {len(attack_sim.honest_nodes)}")
    
    print("3. Computing composite trust matrix...")
    trust_engine = TrustEngine(w_d=0.45, w_i=0.35, w_s=0.20)
    composite_trust = {}
    node_trust = {}
    
    for u in siot.graph.nodes():
        node_scores = []
        for v in siot.graph.nodes():
            if u == v:
                continue
            hist = histories.get((u, v), {"successes": 10, "failures": 1, "direct_trust": 0.8, "recommendations": {}})
            t_dir = hist["direct_trust"]
            t_ind = trust_engine.compute_indirect_trust(u, v, hist["recommendations"], direct_trust)
            s_rel = trust_engine.compute_social_relationship_degree(u, v, siot.graph, siot.edge_attributes)
            t_comp = trust_engine.compute_composite_trust(t_dir, t_ind, s_rel)
            composite_trust[(u, v)] = t_comp
            node_scores.append(t_comp)
        node_trust[u] = float(np.mean(node_scores)) if node_scores else 0.5
        
    class_metrics = compute_trust_classification_metrics(siot.node_attributes, node_trust, threshold=0.55)
    print(f"   Trust classification: F1 = {class_metrics['f1']:.4f}, Precision = {class_metrics['precision']:.4f}, Recall = {class_metrics['recall']:.4f}")
    
    print("4. Testing Path Representation and Decoding...")
    encoder_decoder = PathEncoderDecoder(siot, composite_trust, trust_engine)
    req = siot.generate_service_request()
    src = req["source"]
    dest = req["eligible_providers"][0]
    print(f"   Service Request: Source {src} -> Destination {dest}")
    
    rand_vec = np.random.uniform(0, 1, size=siot.graph.number_of_nodes())
    decoded_path = encoder_decoder.decode(rand_vec, src, dest)
    objs = encoder_decoder.evaluate_objectives(decoded_path)
    print(f"   Decoded Path length: {len(decoded_path)}, Trust: {objs['trust']:.3f}, Latency: {objs['latency']:.1f}ms, Energy: {objs['energy']:.2f}mJ")
    
    print("5. Testing Optimizers (Quick 5 iterations)...")
    dijkstra = DijkstraBaseline(encoder_decoder).optimize(src, dest)
    print(f"   [Dijkstra] Latency: {dijkstra['best_compromise']['objectives']['latency']:.1f}ms, Trust: {dijkstra['best_compromise']['objectives']['trust']:.3f}")
    
    t_greedy = TGreedyBaseline(encoder_decoder).optimize(src, dest)
    print(f"   [T-Greedy] Latency: {t_greedy['best_compromise']['objectives']['latency']:.1f}ms, Trust: {t_greedy['best_compromise']['objectives']['trust']:.3f}")
    
    dbo = DBOptimizer(encoder_decoder, pop_size=10, max_iter=5, seed=123).optimize(src, dest)
    print(f"   [DBO] Pareto Front Size: {len(dbo['pareto_front'])}, Evals: {dbo['eval_count']}")
    
    mpa = MPAOptimizer(encoder_decoder, pop_size=10, max_iter=5, seed=123).optimize(src, dest)
    print(f"   [MPA] Pareto Front Size: {len(mpa['pareto_front'])}, Evals: {mpa['eval_count']}")
    
    hdbo_mpa = HDBOMPAOptimizer(encoder_decoder, pop_size=10, max_iter=5, seed=123).optimize(src, dest)
    print(f"   [HDBO-MPA] Pareto Front Size: {len(hdbo_mpa['pareto_front'])}, Evals: {hdbo_mpa['eval_count']}")
    
    hv = compute_hypervolume(hdbo_mpa['pareto_front'], num_samples=1000)
    print(f"   [HDBO-MPA] Hypervolume: {hv:.4f}")
    print("=== All Modules Passed Smoke Test Successfully! ===")

if __name__ == "__main__":
    import numpy as np
    run_smoke_test()
