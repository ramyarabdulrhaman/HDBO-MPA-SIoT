# SIoT Dataset Data Dictionary

## Node Attributes (`nodes.json`)
| Attribute Name | Data Type | Range / Domain | Units | Description | Provenance |
|---|---|---|---|---|---|
| `node_id` | Integer | $[0, |V|-1]$ | Dimensionless | Unique identifier of the IoT device | SNAP topology |
| `device_type` | String | `sensor`, `smart_device`, `edge_gateway` | Categorical | Hardware class of the IoT device | Simulated (Category B) |
| `supported_services` | List[Integer] | Subset of $\{0, \dots, 11\}$ | Service ID | Standard smart-city service categories hosted | Simulated (Category B) |
| `processing_delay` | Float | $[0.5, 15.0]$ | Milliseconds (ms) | Internal execution/queueing latency per query | Simulated (Category B) |
| `processing_energy` | Float | $[0.05, 2.0]$ | Millijoules (mJ) | Energy dissipated per service execution | Simulated (Category B) |
| `initial_energy` | Float | $[1000, 15000]$ or $\infty$ | Millijoules (mJ) | Device battery capacity (gateways mains-powered) | Simulated (Category B) |
| `residual_energy` | Float | $[0.0, E_{\text{init}}]$ | Millijoules (mJ) | Dynamic available battery during queries | Simulated (Category B) |
| `is_malicious` | Boolean | `True`, `False` | Binary | Ground-truth compromised status | Attack Model (Category C) |
| `attack_type` | String | `none`, `service_drop`, `bad_mouthing`, `ballot_stuffing`, `collusion`, `on_off` | Categorical | Specific adversarial strategy assigned | Attack Model (Category C) |

## Edge Attributes (`edges.json`)
| Attribute Name | Data Type | Range / Domain | Units | Description | Provenance |
|---|---|---|---|---|---|
| `source` | Integer | $[0, |V|-1]$ | Node ID | Originating device of the link | SNAP topology |
| `target` | Integer | $[0, |V|-1]$ | Node ID | Terminating device of the link | SNAP topology |
| `latency` | Float | $[2.0, 35.0]$ | Milliseconds (ms) | Physical one-way transmission latency | Simulated (Category B) |
| `tx_energy` | Float | $[0.10, 0.45]$ | Millijoules (mJ) | Radio energy expended per 2048-bit transmission | Simulated (Category B) |
| `rx_energy` | Float | $0.1024$ | Millijoules (mJ) | Radio energy expended per 2048-bit reception | Simulated (Category B) |
| `bandwidth` | Float | $[10.0, 100.0]$ | Mbps | Available channel transmission capacity | Simulated (Category B) |
| `social_relationships` | List[String] | Subset of `['POR', 'C-WOR', 'CLOR', 'SOR', 'OOR']` | Categorical | Canonical SIoT relationship types active on link | Simulated (Category B) |
| `link_reliability` | Float | $[0.85, 0.99]$ | Dimensionless | Physical frame delivery ratio under normal conditions | Simulated (Category B) |

## Trust History Attributes (`trust_histories.json`)
| Attribute Name | Data Type | Range / Domain | Units | Description | Provenance |
|---|---|---|---|---|---|
| `device_i` | Integer | $[0, |V|-1]$ | Node ID | Requesting/observing IoT device | Simulated (Category C) |
| `device_j` | Integer | $[0, |V|-1]$ | Node ID | Evaluated service provider/neighbor | Simulated (Category C) |
| `successes` ($S_{ij}$) | Integer | $[0, 100]$ | Integer count | Number of successful service transactions | Simulated (Category C) |
| `failures` ($F_{ij}$) | Integer | $[0, 100]$ | Integer count | Number of failed/corrupted service transactions | Simulated (Category C) |
| `recommendations` | Dict[int, float] | Recommender ID $\to [0, 1]$ | Rating | Explicit recommendations $r_{kj}$ from third-party devices | Simulated (Category C) |
| `direct_trust` | Float | $(0, 1)$ | Dimensionless | Laplace-smoothed direct trust score | Derived (Engine) |
| `indirect_trust` | Float | $[0, 1]$ | Dimensionless | Entropy-weighted aggregated recommendation trust | Derived (Engine) |
| `social_similarity` | Float | $[0, 1]$ | Dimensionless | Jaccard social neighborhood similarity | Derived (Engine) |
| `composite_trust` | Float | $[0, 1]$ | Dimensionless | Final multi-factor composite trust score | Derived (Engine) |
