"""
Adversarial Attack Simulation Engine for Social IoT.
Models malicious service providers, bad-mouthing, ballot-stuffing,
coordinated collusion, and on-off strategic misbehavior.
"""

import random
import numpy as np

class AttackSimulator:
    def __init__(self, siot_graph, malicious_ratio=0.20, attack_mode="mixed", seed=42):
        self.graph = siot_graph.graph
        self.node_attributes = siot_graph.node_attributes
        self.malicious_ratio = malicious_ratio
        self.attack_mode = attack_mode
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.malicious_nodes = set()
        self.honest_nodes = set()
        self.collusion_groups = []
        self._assign_malicious_identities()

    def _assign_malicious_identities(self):
        """
        Randomly assigns ground-truth malicious status across the graph population
        according to the designated malicious_ratio and attack_mode.
        """
        all_nodes = list(self.node_attributes.keys())
        num_malicious = int(len(all_nodes) * self.malicious_ratio)
        
        # Pick malicious nodes
        self.malicious_nodes = set(random.sample(all_nodes, num_malicious))
        self.honest_nodes = set(all_nodes) - self.malicious_nodes
        
        mal_list = list(self.malicious_nodes)
        random.shuffle(mal_list)
        
        if self.attack_mode == "mixed":
            # 30% Service Droppers, 25% Bad-Mouthing, 25% Ballot-Stuffing/Collusion, 20% On-Off
            n_drop = int(len(mal_list) * 0.30)
            n_bm = int(len(mal_list) * 0.25)
            n_bs = int(len(mal_list) * 0.25)
            
            drop_nodes = set(mal_list[:n_drop])
            bm_nodes = set(mal_list[n_drop:n_drop + n_bm])
            bs_nodes = set(mal_list[n_drop + n_bm:n_drop + n_bm + n_bs])
            onoff_nodes = set(mal_list[n_drop + n_bm + n_bs:])
            
            for node in all_nodes:
                if node in self.malicious_nodes:
                    self.node_attributes[node]["is_malicious"] = True
                    if node in drop_nodes:
                        self.node_attributes[node]["attack_type"] = "service_drop"
                    elif node in bm_nodes:
                        self.node_attributes[node]["attack_type"] = "bad_mouthing"
                    elif node in bs_nodes:
                        self.node_attributes[node]["attack_type"] = "collusion"
                    else:
                        self.node_attributes[node]["attack_type"] = "on_off"
                else:
                    self.node_attributes[node]["is_malicious"] = False
                    self.node_attributes[node]["attack_type"] = "none"
        else:
            # Isolated attack mode
            for node in all_nodes:
                if node in self.malicious_nodes:
                    self.node_attributes[node]["is_malicious"] = True
                    self.node_attributes[node]["attack_type"] = self.attack_mode
                else:
                    self.node_attributes[node]["is_malicious"] = False
                    self.node_attributes[node]["attack_type"] = "none"

    def generate_interaction_histories(self, num_rounds=100, on_off_state="off", cold_start_ratio=0.60):
        """
        Simulates authentic interaction records (S_ij, F_ij) and peer recommendations (r_kj)
        for active node pairs based on their ground-truth behavior and attack strategies.
        Incorporates cold-start interaction sparsity (cold_start_ratio) where requesters
        lack direct prior history with providers, forcing reliance on recommendations.
        """
        histories = {}
        direct_trust_matrix = {}
        
        # Determine active interaction pairs: all directed edges in G
        pairs_to_generate = set()
        for u, v in self.graph.edges():
            pairs_to_generate.add((u, v))
            pairs_to_generate.add((v, u))
            
        # Also include recommender links
        edge_recommenders = {}
        base_pairs = list(pairs_to_generate)
        for (u, v) in base_pairs:
            neighbors_u = set(self.graph.neighbors(u))
            recs = list(neighbors_u - {v})[:5]
            if len(recs) < 5:
                extra = [n for n in self.graph.neighbors(v) if n != u and n not in recs]
                recs.extend(extra[:min(5 - len(recs), len(extra))])
            edge_recommenders[(u, v)] = recs
            for k in recs:
                pairs_to_generate.add((k, v))
                pairs_to_generate.add((u, k))
                
        for (u, v) in list(pairs_to_generate):
            v_attr = self.node_attributes.get(v, {"is_malicious": False, "attack_type": "none"})
            is_mal = v_attr["is_malicious"]
            atk = v_attr["attack_type"]
            
            # Simulate cold start: with probability cold_start_ratio, u has no prior direct interaction with v
            is_cold_start = (random.random() < cold_start_ratio) and (u != v)
            
            if is_cold_start:
                successes = 0
                failures = 0
                t_dir = 0.50 # Neutral uninformative prior
            else:
                # Determine provider execution success probability
                if not is_mal:
                    p_success = random.uniform(0.88, 0.98)
                else:
                    if atk == "service_drop":
                        p_success = random.uniform(0.05, 0.25) # Massive drop
                    elif atk == "on_off":
                        p_success = random.uniform(0.90, 0.98) if on_off_state == "on" else random.uniform(0.10, 0.30)
                    else:
                        p_success = random.uniform(0.20, 0.40)
                        
                # Sample interaction observations
                num_obs = random.randint(10, 35)
                successes = int(np.random.binomial(num_obs, p_success))
                failures = num_obs - successes
                
                # Direct trust (Laplace smoothed)
                t_dir = (successes + 1.0) / (successes + failures + 2.0)
                
            direct_trust_matrix[(u, v)] = t_dir
            
            histories[(u, v)] = {
                "successes": successes,
                "failures": failures,
                "direct_trust": t_dir,
                "recommendations": {}
            }
            
        # Generate peer recommendations r_kj for evaluating v from perspective of u
        for (u, v) in list(histories.keys()):
            recommenders = edge_recommenders.get((u, v), [])

                
            rec_dict = {}
            for k in recommenders:
                k_attr = self.node_attributes[k]
                k_mal = k_attr["is_malicious"]
                k_atk = k_attr["attack_type"]
                
                v_mal = self.node_attributes[v]["is_malicious"]
                
                if not k_mal:
                    # Honest recommender reflects true historical observation
                    base_rating = direct_trust_matrix.get((k, v), 0.5)
                    rating = float(np.clip(base_rating + random.gauss(0, 0.05), 0.0, 1.0))
                else:
                    # Adversarial recommender
                    if k_atk == "bad_mouthing":
                        if not v_mal:
                            # Slander honest node
                            rating = random.uniform(0.02, 0.18)
                        else:
                            rating = random.uniform(0.70, 0.90)
                    elif k_atk == "collusion" or k_atk == "ballot_stuffing":
                        if v_mal:
                            # Synergistic high score for colluding peer (coordinated low variance)
                            rating = float(np.clip(random.gauss(0.95, 0.015), 0.90, 1.0))
                        else:
                            rating = random.uniform(0.10, 0.30)
                    elif k_atk == "on_off":
                        rating = random.uniform(0.85, 0.95) if on_off_state == "on" else random.uniform(0.10, 0.25)
                    else:
                        rating = random.uniform(0.05, 0.30)
                        
                rec_dict[k] = rating
                
            histories[(u, v)]["recommendations"] = rec_dict
            
        return histories, direct_trust_matrix
