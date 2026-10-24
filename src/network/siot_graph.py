"""
SIoT Graph Generation, Attribute Assignment, and Service Catalog Management.
Implements the formal SIoT graph model G = (V, E) with Atzori relationship taxonomy,
heterogeneous device profiles, and physical QoS/energy models.
"""

import os
import json
import random
import numpy as np
import networkx as nx

class SIoTGraph:
    """
    Represents the Social Internet of Things (SIoT) network graph.
    """
    def __init__(self, name="SIoT_Network", seed=42):
        self.name = name
        self.seed = seed
        self.graph = nx.Graph()
        self.node_attributes = {}
        self.edge_attributes = {}
        self.service_catalog = {}
        self.relationship_types = ['POR', 'C-WOR', 'CLOR', 'SOR', 'OOR']
        self.relationship_weights = {
            'POR': 0.85,    # Parental Object Relationship (same batch/manufacturer)
            'C-WOR': 0.75,  # Co-Work Object Relationship (common tasks)
            'CLOR': 0.65,  # Co-Location Object Relationship (same smart space)
            'SOR': 0.80,   # Social Object Relationship (owner social tie)
            'OOR': 0.95    # Ownership Object Relationship (same owner)
        }
        random.seed(seed)
        np.random.seed(seed)

    @classmethod
    def from_snap_file(cls, filepath, max_nodes=250, seed=42):
        """
        Loads authentic Stanford SNAP graph and extracts a connected subgraph of max_nodes.
        """
        instance = cls(name=f"SNAP_{max_nodes}", seed=seed)
        full_g = nx.read_edgelist(filepath, create_using=nx.Graph(), nodetype=int)
        
        # Select highest degree core node as starting point for breadth-first subgraph
        degrees = dict(full_g.degree())
        start_node = max(degrees, key=degrees.get)
        
        # Extract connected subgraph using BFS traversal to preserve authentic social clustering
        visited = []
        queue = [start_node]
        visited_set = {start_node}
        
        while queue and len(visited) < max_nodes:
            curr = queue.pop(0)
            visited.append(curr)
            neighbors = sorted(list(full_g.neighbors(curr)), key=lambda n: degrees[n], reverse=True)
            for n in neighbors:
                if n not in visited_set and len(visited_set) < max_nodes:
                    visited_set.add(n)
                    queue.append(n)
        
        sub_g = full_g.subgraph(visited).copy()
        
        # Relabel nodes to 0 ... N-1
        mapping = {old_id: new_id for new_id, old_id in enumerate(sorted(sub_g.nodes()))}
        instance.graph = nx.relabel_nodes(sub_g, mapping)
        
        # Ensure single connected component
        if not nx.is_connected(instance.graph):
            largest_cc = max(nx.connected_components(instance.graph), key=len)
            instance.graph = instance.graph.subgraph(largest_cc).copy()
            mapping = {old_id: new_id for new_id, old_id in enumerate(sorted(instance.graph.nodes()))}
            instance.graph = nx.relabel_nodes(instance.graph, mapping)
            
        instance._synthesize_siot_attributes()
        return instance

    @classmethod
    def from_scale_free(cls, n=250, m=8, seed=42):
        """
        Generates a synthetic scale-free Barabási-Albert graph (N nodes, m edges per attachment)
        representing a dense urban SIoT smart-city overlay topology.
        """
        instance = cls(name=f"ScaleFree_{n}", seed=seed)
        instance.graph = nx.barabasi_albert_graph(n, m, seed=seed)
        instance._synthesize_siot_attributes()
        return instance

    def _synthesize_siot_attributes(self):
        """
        Synthesizes documented SIoT device profiles, services, energy, latency,
        and Atzori social relationships on top of the authentic topological graph.
        """
        N = self.graph.number_of_nodes()
        self.node_attributes = {}
        
        # Define 12 smart-city service categories
        num_services = 12
        for s_id in range(num_services):
            self.service_catalog[s_id] = {
                "name": f"SmartCity_Service_{s_id}",
                "base_latency_req": random.uniform(20.0, 60.0),
                "min_trust_req": random.uniform(0.60, 0.75),
                "energy_budget": random.uniform(1.5, 4.0)
            }
            
        # Assign device hardware types: 45% Sensor/Actuator, 35% Smart Device, 20% Edge Gateway
        for node in self.graph.nodes():
            r = random.random()
            if r < 0.45:
                dev_type = "sensor"
                p_delay = random.uniform(5.0, 15.0)       # ms
                p_energy = random.uniform(0.5, 2.0)       # mJ
                init_energy = random.uniform(1000, 3000)  # mJ
                srv_count = random.randint(1, 2)
            elif r < 0.80:
                dev_type = "smart_device"
                p_delay = random.uniform(2.0, 8.0)        # ms
                p_energy = random.uniform(0.2, 1.0)       # mJ
                init_energy = random.uniform(5000, 15000) # mJ
                srv_count = random.randint(2, 4)
            else:
                dev_type = "edge_gateway"
                p_delay = random.uniform(0.5, 2.0)        # ms
                p_energy = random.uniform(0.05, 0.2)      # mJ
                init_energy = float('inf')                # Mains powered
                srv_count = random.randint(4, 7)
                
            supported = sorted(random.sample(range(num_services), srv_count))
            
            self.node_attributes[node] = {
                "node_id": node,
                "device_type": dev_type,
                "processing_delay": p_delay,
                "processing_energy": p_energy,
                "initial_energy": init_energy,
                "residual_energy": init_energy,
                "supported_services": supported,
                "is_malicious": False,
                "attack_type": "none"
            }
            
        # Assign Edge Attributes: Latency, Energy (First-order radio model), Social Ties
        self.edge_attributes = {}
        for u, v in self.graph.edges():
            # Link latency (log-normal distribution)
            latency = float(np.clip(np.random.lognormal(mean=2.2, sigma=0.35), 2.0, 35.0))
            
            # Transmission energy (First order radio model: E_elec * L + eps_amp * L * d^2)
            # Normalized around 0.10 to 0.45 mJ per 2048-bit transmission
            distance = random.uniform(10.0, 50.0) # meters
            tx_energy = (50e-6 * 2048 + 100e-9 * 2048 * (distance**2)) # in mJ
            tx_energy = float(np.clip(tx_energy, 0.10, 0.45))
            rx_energy = 0.1024 # mJ (50e-6 * 2048)
            
            # Bandwidth (Mbps)
            bandwidth = random.uniform(10.0, 100.0)
            
            # Link reliability
            link_reliability = random.uniform(0.90, 0.99)
            
            # Assign Atzori social relationship types
            active_rels = []
            if random.random() < 0.15: active_rels.append('POR')
            if random.random() < 0.25: active_rels.append('C-WOR')
            if random.random() < 0.35: active_rels.append('CLOR')
            if random.random() < 0.40: active_rels.append('SOR')
            if random.random() < 0.10: active_rels.append('OOR')
            if not active_rels:
                active_rels.append(random.choice(['CLOR', 'SOR']))
                
            edge_data = {
                "source": u,
                "target": v,
                "latency": latency,
                "tx_energy": tx_energy,
                "rx_energy": rx_energy,
                "bandwidth": bandwidth,
                "link_reliability": link_reliability,
                "social_relationships": active_rels
            }
            self.edge_attributes[(u, v)] = edge_data
            self.edge_attributes[(v, u)] = edge_data
            
            # Attach to networkx graph
            self.graph[u][v]['latency'] = latency
            self.graph[u][v]['tx_energy'] = tx_energy
            self.graph[u][v]['rx_energy'] = rx_energy
            self.graph[u][v]['bandwidth'] = bandwidth
            self.graph[u][v]['reliability'] = link_reliability
            self.graph[u][v]['relationships'] = active_rels

    def generate_service_request(self, service_id=None, source_node=None, min_hops=2):
        """
        Generates a non-trivial service discovery request where target providers
        are at least min_hops away from the source to prevent trivial 1-hop short circuits.
        """
        if service_id is None:
            service_id = random.choice(list(self.service_catalog.keys()))
            
        all_providers = [
            n for n, attr in self.node_attributes.items()
            if service_id in attr["supported_services"]
        ]
        
        if not all_providers:
            raise ValueError(f"No providers found for service {service_id}")
            
        # Select source and eligible providers meeting the min_hops requirement
        nodes = list(self.graph.nodes())
        attempts = 0
        valid_source = None
        valid_providers = []
        
        while attempts < 100:
            src = source_node if source_node is not None else random.choice(nodes)
            providers_at_dist = []
            for p in all_providers:
                if p != src and nx.has_path(self.graph, src, p):
                    try:
                        dist = nx.shortest_path_length(self.graph, src, p)
                        if dist >= min_hops:
                            providers_at_dist.append(p)
                    except Exception:
                        pass
            if providers_at_dist:
                valid_source = src
                valid_providers = providers_at_dist
                break
            attempts += 1
            if source_node is not None:
                # If specific source requested cannot satisfy min_hops, relax min_hops by 1
                min_hops = max(1, min_hops - 1)
                
        if not valid_providers:
            valid_source = source_node if source_node is not None else random.choice(nodes)
            valid_providers = [p for p in all_providers if p != valid_source]
            
        spec = self.service_catalog[service_id]
        request = {
            "source": valid_source,
            "service_id": service_id,
            "service_name": spec["name"],
            "eligible_providers": valid_providers,
            "max_latency": spec["base_latency_req"] * 1.5,
            "min_trust": spec["min_trust_req"],
            "max_energy": spec["energy_budget"] * 2.0
        }
        return request

    def export_json(self, out_dir):
        """
        Exports the graph instance, node attributes, edge attributes, and service catalog to JSON.
        """
        os.makedirs(out_dir, exist_ok=True)
        nodes_data = [attr for _, attr in sorted(self.node_attributes.items())]
        edges_data = []
        seen = set()
        for (u, v), data in self.edge_attributes.items():
            if (min(u, v), max(u, v)) not in seen:
                seen.add((min(u, v), max(u, v)))
                edges_data.append(data)
                
        with open(os.path.join(out_dir, f"{self.name}_nodes.json"), "w") as f:
            json.dump(nodes_data, f, indent=2)
        with open(os.path.join(out_dir, f"{self.name}_edges.json"), "w") as f:
            json.dump(edges_data, f, indent=2)
        with open(os.path.join(out_dir, f"{self.name}_catalog.json"), "w") as f:
            json.dump(self.service_catalog, f, indent=2)
        print(f"Exported {self.name} to {out_dir}")
