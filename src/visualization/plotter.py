"""
Publication-Quality Visualization Suite for HDBO-MPA SIoT Research.
Strictly plots empirical benchmark data loaded from raw experimental CSV logs.
Zero synthetic equations or hardcoded arrays.
Styles: 300 DPI, academic serif fonts, colorblind-friendly palettes, clean grid.
"""

import os
import sys
import csv
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as ticker

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9.5,
    'figure.titlesize': 14,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'grid.alpha': 0.35,
    'grid.linestyle': '--'
})

COLORS = {
    'HDBO-MPA': '#1f77b4', # Blue
    'DBO': '#ff7f0e',      # Amber
    'MPA': '#2ca02c',      # Green
    'NSGA-II': '#d62728',  # Red
    'MO-PSO': '#9467bd',   # Purple
    'MOEA/D': '#17becf',   # Cyan
    'SPEA2': '#bcbd22',    # Olive
    'MOMPA': '#e377c2',    # Pink
    'ACO': '#8c564b',      # Brown
    'T-Greedy': '#7f7f7f', # Gray
    'Dijkstra': '#333333'  # Dark charcoal
}

def generate_figure_1_architecture(out_dir):
    """Figure 1: Overall SIoT Service-Discovery Architecture."""
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.axis('off')
    
    layers = [
        ("Layer 1: Physical Social IoT Infrastructure", 
         "Heterogeneous Smart-City Devices (Sensors, Edge Gateways, Mobile Smart Objects)\nWireless Communication Links (Latency, Energy, Bandwidth) | 5 Atzori Social Ties (POR, C-WOR, CLOR, SOR, OOR)", 0.78, '#e8f4f8'),
        ("Layer 2: Trust Computation & Adversarial Defense Engine", 
         "Laplace Direct Interaction Trust | Shannon Entropy-Modulated Indirect Recommendation Filtering\nRobust Median/MAD Consensus Divergence Penalties (Combats Collusion, Bad-Mouthing, Ballot-Stuffing) | Jaccard Social Proximity", 0.50, '#fef9e7'),
        ("Layer 3: Multi-Objective Combinatorial Path Optimization (HDBO-MPA)", 
         "Exploratory Sub-pop (DBO: Rolling, Dancing, Breeding) | Exploitative Sub-pop (MPA: Brownian & Scale-Free Lévy Flights)\nGraph-Constrained Random-Key Priority Decoder with Wilson Loop-Erasure | Shared Non-Dominated Pareto Archive", 0.22, '#eafaf1'),
        ("Layer 4: Operational Service Delivery & Decision Selection", 
         "Non-Dominated Pareto Frontier (Trust, Latency, Energy, QoS) | Multi-Criteria Compromise Path (TOPSIS Decision Policy)", -0.06, '#fbf0f0')
    ]
    
    for title, desc, y_pos, color in layers:
        rect = FancyBboxPatch((0.05, y_pos), 0.90, 0.20, boxstyle="round,pad=0.03", 
                              ec="#2c3e50", fc=color, lw=1.5)
        ax.add_patch(rect)
        ax.text(0.50, y_pos + 0.15, title, ha='center', va='center', weight='bold', fontsize=12, color='#1a252f')
        ax.text(0.50, y_pos + 0.07, desc, ha='center', va='center', fontsize=9.5, color='#34495e', multialignment='center')
        
    for y_start, y_end in [(0.77, 0.71), (0.49, 0.43), (0.21, 0.15)]:
        ax.annotate('', xy=(0.50, y_end), xytext=(0.50, y_start),
                    arrowprops=dict(facecolor='#2c3e50', edgecolor='#2c3e50', width=2, headwidth=8))
                    
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.15, 1.05)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_1_architecture.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_2_trust_pipeline(out_dir):
    """Figure 2: Trust Computation Pipeline."""
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.axis('off')
    
    boxes = [
        ("1. Direct Trust ($T_{dir}$)", 
         "Laplace Smoothing\n$T_{dir} = \\frac{S+1}{S+F+2}$\nTemporal Decay $\\lambda_{rec}$", 
         0.04, 0.19, '#d4efdf'),
        ("2. Indirect Trust ($T_{ind}$)", 
         "Recommender Set $\\mathcal{R}_{ij}$\nEntropy $H_{ij} = -\\sum p_b \\log_2 p_b$\nRobust Median/MAD Consensus", 
         0.29, 0.19, '#d6eaf8'),
        ("3. Social Trust ($S_{rel}$)", 
         "Atzori Social Relations\nJaccard Co-location $J(u, v)$\nObject Ownership $OOR$", 
         0.54, 0.19, '#fcf3cf'),
        ("4. Composite Trust ($T_{comp}$)", 
         "$T_{comp} = w_d T_{dir} + w_i T_{ind} + w_s S_{rel}$\nStrictly Monotonic Objective\n$f_T(P) = 0.75\\bar{T} + 0.25 T_{min} - \\text{pen}$", 
         0.79, 0.18, '#fadbd8')
    ]
    
    for title, desc, x_pos, width, color in boxes:
        rect = FancyBboxPatch((x_pos, 0.25), width, 0.52, boxstyle="round,pad=0.03", 
                              ec="#2c3e50", fc=color, lw=1.5)
        ax.add_patch(rect)
        ax.text(x_pos + width/2, 0.68, title, ha='center', va='center', weight='bold', fontsize=11, color='#1a252f')
        ax.text(x_pos + width/2, 0.45, desc, ha='center', va='center', fontsize=9.2, color='#34495e', multialignment='center')
        
    for x_arr in [0.245, 0.495, 0.745]:
        ax.annotate('', xy=(x_arr + 0.035, 0.51), xytext=(x_arr - 0.015, 0.51),
                    arrowprops=dict(facecolor='#2c3e50', edgecolor='#2c3e50', width=2, headwidth=7))
                    
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0.15, 0.88)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_2_trust_pipeline.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_3_workflow(out_dir):
    """Figure 3: Hybrid Co-Evolutionary Optimization Flowchart."""
    fig, ax = plt.subplots(figsize=(13.6, 7.4), dpi=300)
    ax.axis('off')
    
    ax.set_xlim(-0.3, 13.5)
    ax.set_ylim(-0.4, 7.4)
    
    c_blue = {'bg': '#F1F5F9', 'border': '#1E3A8A', 'head': '#1E3A8A'}
    c_amber = {'bg': '#FFFBEB', 'border': '#B45309', 'head': '#92400E'}
    c_green = {'bg': '#F0FDF4', 'border': '#15803D', 'head': '#166534'}
    c_purple = {'bg': '#FAF5FF', 'border': '#7E22CE', 'head': '#6B21A8'}
    c_teal = {'bg': '#F0FDFA', 'border': '#0F766E', 'head': '#115E59'}

    def draw_card(x, y, w, h, c_dict, title, items):
        shadow = FancyBboxPatch((x + 0.05, y - 0.05), w, h, boxstyle="round,pad=0.06,rounding_size=0.15",
                                fc='#CBD5E1', ec='none', zorder=1)
        ax.add_patch(shadow)
        
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.15",
                              fc=c_dict['bg'], ec=c_dict['border'], lw=1.8, zorder=2)
        ax.add_patch(rect)
        
        h_h = 0.52
        banner = FancyBboxPatch((x, y + h - h_h), w, h_h, boxstyle="round,pad=0.06,rounding_size=0.15",
                                fc=c_dict['border'], ec='none', zorder=3)
        ax.add_patch(banner)
        ax.fill_between([x - 0.06, x + w + 0.06], [y + h - h_h, y + h - h_h], [y + h - h_h + 0.15, y + h - h_h + 0.15],
                        color=c_dict['border'], zorder=3)
        
        ax.text(x + w/2.0, y + h - h_h/2.0, title, ha='center', va='center',
                weight='bold', fontsize=9.5, color='white', zorder=4)
        
        curr_y = y + h - h_h - 0.28
        for item in items:
            if item.startswith("###"):
                text = item.replace("###", "").strip()
                ax.text(x + 0.14, curr_y, text, ha='left', va='center',
                        weight='bold', fontsize=8.5, color=c_dict['head'], zorder=4)
                curr_y -= 0.26
            elif item == "":
                curr_y -= 0.12
            else:
                ax.text(x + 0.14, curr_y, item, ha='left', va='center',
                        fontsize=7.8, color='#0F172A', zorder=4)
                curr_y -= 0.23

    s1_items = [
        "### Graph & Trust Setup",
        "• Network Topology G = (V, E)",
        "• Composite Trust Matrix T_comp",
        "• Pairwise Social Proximities S_rel",
        "",
        "### Swarm Partitioning",
        "• N = 100 Agents in [0, 1]^|V|",
        "• DBO Sub-Swarm: N_dbo = 50",
        "• MPA Sub-Swarm: N_mpa = 50",
        "• Sample Guide X_best from Archive"
    ]
    draw_card(0.2, 0.2, 2.3, 5.4, c_blue, "STAGE 1: INITIALIZATION", s1_items)

    s2a_items = [
        "### Global Exploration Operators",
        "• Ball-Rolling (p = 0.30): Celestial navigation",
        "• Obstacle Dancing: θ ∈ (0, π] reorientation",
        "• Dynamic Breeding: Spatially bounded zone",
        "• Stealing Regimes: Foraging across best food"
    ]
    draw_card(3.1, 3.2, 3.4, 2.4, c_amber, "STAGE 2A: DBO EXPLORATION", s2a_items)

    s2b_items = [
        "### Multi-Regime Exploitation",
        "• Phase 1 (t < T_max/3): High velocity Brownian",
        "• Phase 2 (T/3 ≤ t < 2T/3): Mixed Lévy + Brownian",
        "• Phase 3 (t ≥ 2T_max/3): Scale-free Lévy flights",
        "• FADs Perturbation: Triggers if HV stalls ≥ 3 iters"
    ]
    draw_card(3.1, 0.2, 3.4, 2.4, c_green, "STAGE 2B: MPA EXPLOITATION", s2b_items)

    badge = FancyBboxPatch((3.7, 2.68), 2.2, 0.42, boxstyle="round,pad=0.04,rounding_size=0.1",
                           fc='#EFF6FF', ec='#2563EB', lw=1.2, zorder=5)
    ax.add_patch(badge)
    ax.text(4.8, 2.89, "⇄ Co-Evolution & Elite Exchange", ha='center', va='center',
            weight='bold', fontsize=7.5, color='#1D4ED8', zorder=6)

    s3_items = [
        "### Random-Key Priority Decoder",
        "• Maps continuous vector X[u] to graph",
        "• Priority Score Formulation:",
        "  Score(u) = 0.5 X[u] + 0.3 T_comp(v, u)",
        "           + 0.2 [ L_bar / (l_vu + L_bar) ]",
        "",
        "### Wilson's Loop-Erasure Repair",
        "• Tracks visited hops chronologically",
        "• Erases cyclic loops instantaneously",
        "",
        "### Dijkstra Residual Fallback",
        "• Activates upon reaching dead-end node",
        "• Guarantees 100% path feasibility"
    ]
    draw_card(7.1, 0.2, 2.8, 5.4, c_purple, "STAGE 3: PATH DECODING & REPAIR", s3_items)

    s4_items = [
        "### Multi-Objective Evaluation",
        "• Trustworthiness: Maximize f_T(P)",
        "• Latency: Minimize f_L(P) (ms)",
        "• Energy: Minimize f_E(P) (mJ)",
        "• Reliability: Maximize f_Q(P)",
        "",
        "### Pareto Archive Maintenance",
        "• Non-dominated Pareto sorting",
        "• Crowding distance pruning (C = 50)",
        "",
        "### TOPSIS Decision Engine",
        "• Distance to ideal best & worst",
        "• Selects optimal deployment path P*"
    ]
    draw_card(10.5, 0.2, 2.6, 5.4, c_teal, "STAGE 4: PARETO & TOPSIS", s4_items)

    arrow_props = dict(facecolor='#1E293B', edgecolor='#1E293B', width=1.8, headwidth=6.0, headlength=6.5, zorder=5)
    
    ax.annotate('', xy=(3.05, 4.4), xytext=(2.55, 3.8), arrowprops=arrow_props)
    ax.text(2.60, 4.45, "N_dbo", fontsize=7.6, weight='bold', color='#B45309', zorder=6)
    
    ax.annotate('', xy=(3.05, 1.4), xytext=(2.55, 2.0), arrowprops=arrow_props)
    ax.text(2.60, 1.30, "N_mpa", fontsize=7.6, weight='bold', color='#15803D', zorder=6)

    ax.annotate('', xy=(7.05, 3.9), xytext=(6.55, 4.4), arrowprops=arrow_props)
    ax.annotate('', xy=(7.05, 2.0), xytext=(6.55, 1.4), arrowprops=arrow_props)

    ax.annotate('', xy=(10.45, 2.9), xytext=(9.95, 2.9), arrowprops=arrow_props)
    ax.text(10.2, 3.12, "Routes", ha='center', fontsize=7.2, weight='bold', color='#475569')

    ax.plot([11.8, 11.8, 10.1], [5.6, 6.55, 6.55], color='#DC2626', lw=2.0, zorder=7)
    ax.plot([6.5, 4.8, 4.8], [6.55, 6.55, 5.65], color='#DC2626', lw=2.0, zorder=7)
    
    ax.annotate('', xy=(4.8, 5.62), xytext=(4.8, 5.75),
                arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=2.0, headwidth=6.5, headlength=6.0, zorder=8))
    
    f_box = FancyBboxPatch((6.5, 6.32), 3.6, 0.46, boxstyle="round,pad=0.04,rounding_size=0.1",
                           fc='#FEF2F2', ec='#DC2626', lw=1.5, zorder=9)
    ax.add_patch(f_box)
    ax.text(8.3, 6.55, "Elite Guide X_best Feedback Loop (t = 1 ... T_max)",
            ha='center', va='center', weight='bold', fontsize=7.8, color='#991B1B', zorder=10)

    ax.annotate('', xy=(11.8, -0.32), xytext=(11.8, 0.15),
                arrowprops=dict(facecolor='#0F766E', edgecolor='#0F766E', width=2.6, headwidth=7.5, zorder=7))
    out_box = FancyBboxPatch((10.3, -0.36), 3.0, 0.42, boxstyle="round,pad=0.04,rounding_size=0.1",
                            fc='#0F766E', ec='none', zorder=8)
    ax.add_patch(out_box)
    ax.text(11.8, -0.15, "Optimal Operational Route P*", ha='center', va='center',
            weight='bold', fontsize=8.5, color='white', zorder=9)

    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_3_workflow.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_4_information_flow(out_dir):
    """Figure 4: Inter-Population Information Exchange Mechanism."""
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.axis('off')
    
    rect_dbo = FancyBboxPatch((0.08, 0.45), 0.32, 0.42, boxstyle="round,pad=0.03", ec="#d35400", fc="#fbeee6", lw=1.5)
    ax.add_patch(rect_dbo)
    ax.text(0.24, 0.78, "Exploratory Sub-population\n(Dung Beetle Optimizer)", ha='center', va='center', weight='bold', fontsize=11, color='#a04000')
    ax.text(0.24, 0.58, "• Rolling & Dancing Operators\n• Breeding & Stealing Regimes\n• Broad Global Diversity", ha='center', va='center', fontsize=9.2)

    rect_mpa = FancyBboxPatch((0.60, 0.45), 0.32, 0.42, boxstyle="round,pad=0.03", ec="#27ae60", fc="#eafaf1", lw=1.5)
    ax.add_patch(rect_mpa)
    ax.text(0.76, 0.78, "Exploitative Sub-population\n(Marine Predators Algorithm)", ha='center', va='center', weight='bold', fontsize=11, color='#1e8449')
    ax.text(0.76, 0.58, "• Brownian & Lévy Flights\n• FADs Effect & Eddy Formation\n• High-Precision Refinement", ha='center', va='center', fontsize=9.2)

    rect_arch = FancyBboxPatch((0.25, 0.06), 0.50, 0.24, boxstyle="round,pad=0.03", ec="#2980b9", fc="#ebf5fb", lw=1.5)
    ax.add_patch(rect_arch)
    ax.text(0.50, 0.22, "Shared Non-Dominated External Pareto Archive", ha='center', va='center', weight='bold', fontsize=11, color='#1f618d')
    ax.text(0.50, 0.12, "Crowding Distance Elite Selection | Cross-Subpopulation Exchange on Stagnation", ha='center', va='center', fontsize=9)

    ax.annotate('', xy=(0.38, 0.31), xytext=(0.32, 0.45),
                arrowprops=dict(facecolor='#d35400', edgecolor='#d35400', width=1.5, headwidth=6))
    ax.annotate('', xy=(0.62, 0.31), xytext=(0.68, 0.45),
                arrowprops=dict(facecolor='#27ae60', edgecolor='#27ae60', width=1.5, headwidth=6))
    ax.annotate('', xy=(0.16, 0.45), xytext=(0.28, 0.31),
                arrowprops=dict(facecolor='#2980b9', edgecolor='#2980b9', width=1.5, headwidth=6))
    ax.annotate('', xy=(0.84, 0.45), xytext=(0.72, 0.31),
                arrowprops=dict(facecolor='#2980b9', edgecolor='#2980b9', width=1.5, headwidth=6))
                
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.98)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_4_information_flow.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_5_path_repair(out_dir):
    """Figure 5: Graph-based Path Representation, Decoding, and Repair Mechanism."""
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    ax.axis('off')
    
    rect_vec = FancyBboxPatch((0.05, 0.68), 0.90, 0.20, boxstyle="round,pad=0.02", ec='#34495e', fc='#f4f6f7', lw=1.5)
    ax.add_patch(rect_vec)
    ax.text(0.50, 0.81, "Continuous Random-Key Priority Vector $\\mathbf{x} \\in [0, 1]^{|V|}$", ha='center', weight='bold', fontsize=11)
    ax.text(0.50, 0.73, "[$v_0$: 0.82, $v_1$: 0.14, $v_2$: 0.95, $v_3$: 0.43, $v_4$: 0.88, $v_5$: 0.31, ..., $v_n$: 0.76]", 
            ha='center', fontsize=9.5, family='monospace')
            
    rect_dec = FancyBboxPatch((0.05, 0.34), 0.42, 0.25, boxstyle="round,pad=0.02", ec='#2980b9', fc='#ebf5fb', lw=1.5)
    ax.add_patch(rect_dec)
    ax.text(0.26, 0.51, "Greedy Topological Traversal", ha='center', weight='bold', fontsize=10.5, color='#2980b9')
    ax.text(0.26, 0.41, "Next hop $u = \\arg\\max [0.5 x_u + 0.3 T + 0.2 \\frac{\\bar{L}}{\\ell+\\bar{L}}]$", ha='center', fontsize=9)
    
    rect_loop = FancyBboxPatch((0.53, 0.34), 0.42, 0.25, boxstyle="round,pad=0.02", ec='#c0392b', fc='#fdedec', lw=1.5)
    ax.add_patch(rect_loop)
    ax.text(0.74, 0.51, "Wilson Loop-Erasure & Fallback", ha='center', weight='bold', fontsize=10.5, color='#c0392b')
    ax.text(0.74, 0.41, "Cycle $(v_i, ..., v_j) \\to (v_i, v_{j+1})$ spliced instantly\nDijkstra fallback ensures 100% feasibility", ha='center', fontsize=9)
    
    rect_out = FancyBboxPatch((0.10, 0.05), 0.80, 0.20, boxstyle="round,pad=0.02", ec='#27ae60', fc='#eafaf1', lw=1.5)
    ax.add_patch(rect_out)
    ax.text(0.50, 0.17, "100% Feasible Loop-Free Service Path $P = (s, v_2, v_4, ..., t)$", ha='center', weight='bold', fontsize=11, color='#27ae60')
    ax.text(0.50, 0.09, "Satisfies Latency Constraint $\\mathcal{C}_L$, Energy $\\mathcal{C}_E$, Trust Threshold $\\mathcal{C}_T$, and Connectivity", ha='center', fontsize=9.5)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0.01, 0.94)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_5_path_repair.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_6_pareto_front(csv_path, out_dir):
    """Figure 6: Example Pareto Front Showing Trust, Latency, and Energy Trade-Offs."""
    fig = plt.figure(figsize=(9.2, 6.2))
    ax = fig.add_subplot(111, projection='3d')
    
    if os.path.exists(csv_path):
        data = {}
        with open(csv_path, "r") as f:
            for row in csv.DictReader(f):
                alg = row["algorithm"]
                if alg not in data:
                    data[alg] = {"trust": [], "latency": [], "energy": []}
                data[alg]["trust"].append(float(row["best_trust"]))
                data[alg]["latency"].append(float(row["best_latency"]))
                data[alg]["energy"].append(float(row["best_energy"]))
                
        for alg in ["HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO"]:
            if alg in data:
                ax.scatter(data[alg]["latency"], data[alg]["energy"], data[alg]["trust"],
                           label=alg, color=COLORS.get(alg, '#333'), s=40, alpha=0.85, edgecolors='k', linewidth=0.5)
    ax.set_xlabel('End-to-End Latency (ms)', labelpad=10)
    ax.set_ylabel('Energy Consumption (mJ)', labelpad=10)
    ax.set_zlabel('Composite Trust Score', labelpad=14)
    ax.view_init(elev=25, azim=135)
    ax.legend(loc='upper right', framealpha=0.92, fontsize=9.5)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_6_pareto_front.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_7_convergence(conv_csv, out_dir):
    """Figure 7: Hypervolume Convergence Curves Loaded from CSV."""
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    
    if os.path.exists(conv_csv):
        data = {}
        with open(conv_csv, "r") as f:
            for r in csv.DictReader(f):
                alg = r["algorithm"]
                if alg not in data:
                    data[alg] = {"evals": [], "hv": []}
                data[alg]["evals"].append(int(r["eval_count"]))
                data[alg]["hv"].append(float(r["hypervolume"]))
                
        for alg, vals in data.items():
            ax.plot(vals["evals"], vals["hv"], label=alg, color=COLORS.get(alg, '#333'), lw=2.2, marker='o', markersize=4)
    else:
        ax.text(0.5, 0.5, "Convergence Log Not Found", ha='center', va='center')
        
    ax.set_xlabel('Objective Function Evaluations')
    ax.set_ylabel('Hypervolume (HV) Indicator')
    ax.grid(True)
    ax.legend(loc='lower right', framealpha=0.92)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_7_convergence.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_8_malicious_ratio(attack_csv, out_dir):
    """Figure 8: Trust Performance Under Increasing Malicious-Node Proportions."""
    fig, ax1 = plt.subplots(figsize=(8.5, 5.2))
    
    if os.path.exists(attack_csv):
        records = []
        with open(attack_csv, "r") as f:
            for r in csv.DictReader(f):
                if r["attack_mode"] == "mixed":
                    records.append(r)
                    
        ratios = [int(float(r["malicious_ratio"])*100) for r in records]
        f1_prop = [float(r["prop_f1"]) for r in records]
        f1_beta = [float(r["beta_f1"]) for r in records]
        f1_eigen = [float(r["eigen_f1"]) for r in records]
        far_prop = [float(r["prop_far"]) for r in records]
        latencies = [float(r["avg_latency"]) for r in records]
        
        l1 = ax1.plot(ratios, f1_prop, label='Proposed Engine (F1)', color='#1f77b4', lw=2.5, marker='o')
        l2 = ax1.plot(ratios, f1_beta, label='Beta-Reputation (F1)', color='#ff7f0e', lw=2.0, marker='s', ls='--')
        l3 = ax1.plot(ratios, f1_eigen, label='EigenTrust (F1)', color='#2ca02c', lw=2.0, marker='^', ls=':')
        l4 = ax1.plot(ratios, far_prop, label='False Acceptance Rate (FAR)', color='#d62728', lw=2.0, marker='d')
        
        ax1.set_xlabel('Malicious Node Proportion (%)', fontsize=10.5)
        ax1.set_ylabel('Trust Performance Metric Score', fontsize=10.5)
        ax1.set_ylim(0.0, 1.05)
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        l5 = ax2.plot(ratios, latencies, label='End-to-End Latency (ms)', color='#8e44ad', lw=2.2, marker='x', ls='-.')
        ax2.set_ylabel('End-to-End Latency (ms)', color='#8e44ad', fontsize=10.5)
        ax2.tick_params(axis='y', labelcolor='#8e44ad')
        
        lines = l1 + l2 + l3 + l4 + l5
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='lower left', framealpha=0.92, fontsize=8.8)
        
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_8_malicious_ratio.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_9_sdsr_attack(attack_csv, out_dir):
    """Figure 9: Service Discovery Success Rate Under Attack (SDSR-A)."""
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    
    if os.path.exists(attack_csv):
        modes_to_plot = ["mixed", "service_drop", "bad_mouthing", "collusion", "on_off", "sybil"]
        data_by_mode = {}
        with open(attack_csv, "r") as f:
            for r in csv.DictReader(f):
                m = r["attack_mode"]
                if m not in data_by_mode:
                    data_by_mode[m] = {"ratios": [], "sdsr": [], "true_del": []}
                data_by_mode[m]["ratios"].append(int(float(r["malicious_ratio"])*100))
                data_by_mode[m]["sdsr"].append(float(r["sdsr_a"])*100)
                data_by_mode[m]["true_del"].append(float(r["true_delivery_rate"])*100)
                
        for m in modes_to_plot:
            if m in data_by_mode:
                ax.plot(data_by_mode[m]["ratios"], data_by_mode[m]["sdsr"], label=f"SDSR-A: {m}", lw=2.0, marker='o')
                
    ax.set_xlabel('Malicious Node Proportion (%)')
    ax.set_ylabel('Service Discovery Success Rate Under Attack - SDSR-A (%)')
    ax.grid(True)
    ax.legend(loc='lower left', framealpha=0.92, fontsize=8.5)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_9_sdsr_attack.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_10_latency_vs_nodes(sc_csv, out_dir):
    """Figure 10: Discovery Latency versus Graph Size."""
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    
    if os.path.exists(sc_csv):
        data = {}
        with open(sc_csv, "r") as f:
            for r in csv.DictReader(f):
                alg = r["algorithm"]
                if alg not in data:
                    data[alg] = {"nodes": [], "latency": []}
                data[alg]["nodes"].append(int(r["nodes"]))
                data[alg]["latency"].append(float(r["latency"]))
                
        for alg, vals in data.items():
            ax.plot(vals["nodes"], vals["latency"], label=alg, color=COLORS.get(alg, '#333'), lw=2.2, marker='o')
            
    ax.set_xlabel('Network Size (|V| Nodes)')
    ax.set_ylabel('End-to-End Discovery Latency (ms)')
    ax.grid(True)
    ax.legend(loc='upper left', framealpha=0.92)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_10_latency_vs_nodes.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_11_energy_lifetime(bench_csv, out_dir):
    """Figure 11: Energy Per Query and End-to-End Latency Trade-Offs."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8))
    
    if os.path.exists(bench_csv):
        data = {}
        with open(bench_csv, "r") as f:
            for r in csv.DictReader(f):
                alg = r["algorithm"]
                if alg not in data:
                    data[alg] = {"energy": [], "latency": []}
                data[alg]["energy"].append(float(r["best_energy"]))
                data[alg]["latency"].append(float(r["best_latency"]))
                
        algs = [a for a in ["HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", "MOEA/D", "SPEA2", "MOMPA"] if a in data]
        mean_energies = [np.mean(data[a]["energy"]) for a in algs]
        mean_latencies = [np.mean(data[a]["latency"]) for a in algs]
        
        bar_colors = [COLORS.get(a, '#333') for a in algs]
        ax1.bar(algs, mean_energies, color=bar_colors, edgecolor='k', linewidth=0.8, alpha=0.85)
        ax1.set_ylabel('Energy Per Query (mJ)')
        ax1.set_xticks(range(len(algs)))
        ax1.set_xticklabels(algs, rotation=35, ha='right')
        ax1.grid(True, axis='y')
        
        ax2.bar(algs, mean_latencies, color=bar_colors, edgecolor='k', linewidth=0.8, alpha=0.85)
        ax2.set_ylabel('Path Latency (ms)')
        ax2.set_xticks(range(len(algs)))
        ax2.set_xticklabels(algs, rotation=35, ha='right')
        ax2.grid(True, axis='y')
        
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_11_energy_lifetime.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_12_hypervolume_distribution(bench_csv, out_dir):
    """Figure 12: Empirical Hypervolume Distribution across 30 Runs."""
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    
    if os.path.exists(bench_csv):
        data = {}
        with open(bench_csv, "r") as f:
            for r in csv.DictReader(f):
                alg = r["algorithm"]
                if alg not in data:
                    data[alg] = []
                data[alg].append(float(r["hypervolume"]))
                
        algs = [a for a in ["HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", "MOEA/D", "SPEA2", "MOMPA"] if a in data]
        box_data = [data[a] for a in algs]
        
        bp = ax.boxplot(box_data, tick_labels=algs, patch_artist=True, medianprops=dict(color='black', lw=1.5))
        for patch, alg in zip(bp['boxes'], algs):
            patch.set_facecolor(COLORS.get(alg, '#3498db'))
            patch.set_alpha(0.80)
            
    ax.set_ylabel('Hypervolume (HV) Indicator')
    ax.set_xticklabels(algs, rotation=30, ha='right')
    ax.grid(True, axis='y')
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_12_qos_satisfaction.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_13_ablation(ablation_csv, out_dir):
    """Figure 13: Ablation Study Visualization across A0 - A10."""
    fig, ax = plt.subplots(figsize=(11.0, 5.2))
    
    if os.path.exists(ablation_csv):
        data = {}
        with open(ablation_csv, "r") as f:
            for r in csv.DictReader(f):
                code = r["ablation_code"]
                if code not in data:
                    data[code] = []
                data[code].append(float(r["hypervolume"]))
                
        codes = [
            "A0_Full_HDBO_MPA", "A1_DBO_Only", "A2_MPA_Only", "A3_No_Entropy_Weighting",
            "A4_Direct_Trust_Only", "A5_No_Social_Relationship", "A6_No_Indirect_Trust",
            "A7_Sequential_Hybrid", "A8_Random_Selection", "A9_No_Loop_Erasure", "A10_No_Archive_Crowding"
        ]
        short_labels = [
            "A0 (Full)", "A1 (DBO)", "A2 (MPA)", "A3 (No Ent)", "A4 (Dir Only)",
            "A5 (No Soc)", "A6 (No Ind)", "A7 (Seq)", "A8 (Rand Key)", "A9 (No Loop Er)", "A10 (No Crowding)"
        ]
        
        means = [np.mean(data[c]) if c in data else 0.0 for c in codes]
        stds = [np.std(data[c]) if c in data else 0.0 for c in codes]
        
        x = np.arange(len(codes))
        bars = ax.bar(x, means, yerr=stds, capsize=4, color='#3498db', edgecolor='#2c3e50', linewidth=0.8, alpha=0.85)
        ax.set_ylabel('Hypervolume (HV) Indicator')
        ax.set_xticks(x)
        ax.set_xticklabels(short_labels, rotation=35, ha='right', fontsize=9)
        
        for i, (m, s) in enumerate(zip(means, stds)):
            ax.text(i, m + s + 0.005, f"{m:.3f}", ha='center', va='bottom', fontsize=8.5, weight='bold')
            
        ax.grid(True, axis='y')
        
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_13_ablation.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_14_sensitivity(sens_csv, out_dir):
    """Figure 14: Sensitivity of Hypervolume to Obstacle Dance Probability p and Lévy Index beta."""
    fig = plt.figure(figsize=(9.2, 6.2))
    ax = fig.add_subplot(111, projection='3d')
    
    if os.path.exists(sens_csv):
        p_vals = []
        beta_vals = []
        hv_vals = []
        with open(sens_csv, "r") as f:
            for r in csv.DictReader(f):
                if r.get("category") == "dance_levy_surface":
                    p_vals.append(float(r["param1"]))
                    beta_vals.append(float(r["param2"]))
                    hv_vals.append(float(r["hypervolume"]))
                    
        if p_vals:
            # Triangulated surface from empirical points
            p_arr = np.array(p_vals)
            beta_arr = np.array(beta_vals)
            hv_arr = np.array(hv_vals)
            surf = ax.plot_trisurf(p_arr, beta_arr, hv_arr, cmap='viridis', edgecolor='none', alpha=0.90)
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Hypervolume (HV)')
            
    ax.set_xlabel('Obstacle Dancing Prob ($p$)', labelpad=10)
    ax.set_ylabel('Lévy Flight Index ($\\beta$)', labelpad=10)
    ax.set_zlabel('Hypervolume (HV)', labelpad=10)
    ax.view_init(elev=30, azim=45)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_14_sensitivity.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_15_runtime_evals(bench_csv, out_dir):
    """Figure 15: Runtime and Objective Evaluations Comparison."""
    fig, ax1 = plt.subplots(figsize=(8.5, 5.0))
    
    if os.path.exists(bench_csv):
        data = {}
        with open(bench_csv, "r") as f:
            for r in csv.DictReader(f):
                alg = r["algorithm"]
                if alg not in data:
                    data[alg] = {"runtime": [], "evals": []}
                data[alg]["runtime"].append(float(r["runtime_sec"]))
                data[alg]["evals"].append(int(r["eval_count"]))
                
        algs = [a for a in ["HDBO-MPA", "DBO", "MPA", "NSGA-II", "MO-PSO", "MOEA/D", "SPEA2", "MOMPA"] if a in data]
        mean_rt = [np.mean(data[a]["runtime"]) for a in algs]
        mean_ev = [np.mean(data[a]["evals"]) for a in algs]
        
        x = np.arange(len(algs))
        width = 0.35
        
        b1 = ax1.bar(x - width/2, mean_rt, width, label='Runtime (s)', color='#2980b9', edgecolor='k', alpha=0.85)
        ax1.set_ylabel('Execution Runtime (seconds)', color='#2980b9')
        ax1.tick_params(axis='y', labelcolor='#2980b9')
        ax1.set_xticks(x)
        ax1.set_xticklabels(algs, rotation=35, ha='right')
        
        ax2 = ax1.twinx()
        b2 = ax2.bar(x + width/2, mean_ev, width, label='Objective Evaluations', color='#e67e22', edgecolor='k', alpha=0.85)
        ax2.set_ylabel('Objective Function Evaluations', color='#e67e22')
        ax2.tick_params(axis='y', labelcolor='#e67e22')
        
        lines = [b1, b2]
        labels = ['Runtime (s)', 'Objective Evaluations']
        ax1.legend(lines, labels, loc='upper left', framealpha=0.92)
        
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_15_runtime_evals.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_figure_16_scalability_dense(sc_csv, out_dir):
    """Figure 16: Scalability across Graph Sizes and Node Density."""
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    
    if os.path.exists(sc_csv):
        nodes = []
        runtimes = []
        with open(sc_csv, "r") as f:
            for r in csv.DictReader(f):
                if r["algorithm"] == "HDBO-MPA":
                    nodes.append(int(r["nodes"]))
                    runtimes.append(float(r["runtime_sec"]))
                    
        if nodes:
            ax.plot(nodes, runtimes, label='HDBO-MPA Runtime (SNAP ego-Facebook)', marker='o', lw=2.5, color='#1f77b4')
            
    ax.set_xlabel('Network Size (|V| Nodes)')
    ax.set_ylabel('Optimization Runtime (seconds)')
    ax.grid(True)
    ax.legend(loc='upper left', framealpha=0.92)
    plt.tight_layout()
    out_file = os.path.join(out_dir, "figure_16_scalability.png")
    plt.savefig(out_file)
    plt.close()
    print(f"Generated: {out_file}")

def generate_all_figures(data_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print("Generating all 16 scientific figures from empirical logs...")
    generate_figure_1_architecture(out_dir)
    generate_figure_2_trust_pipeline(out_dir)
    generate_figure_3_workflow(out_dir)
    generate_figure_4_information_flow(out_dir)
    generate_figure_5_path_repair(out_dir)
    
    bench_csv = os.path.join(data_dir, "experiments", "raw_results", "multi_objective_benchmark_raw.csv")
    conv_csv = os.path.join(data_dir, "experiments", "raw_results", "convergence_raw.csv")
    attack_csv = os.path.join(data_dir, "experiments", "raw_results", "attack_resilience_raw.csv")
    sc_csv = os.path.join(data_dir, "experiments", "raw_results", "scalability_raw.csv")
    abl_csv = os.path.join(data_dir, "experiments", "raw_results", "ablation_study_raw.csv")
    sens_csv = os.path.join(data_dir, "experiments", "raw_results", "sensitivity_analysis_raw.csv")
    
    generate_figure_6_pareto_front(bench_csv, out_dir)
    generate_figure_7_convergence(conv_csv, out_dir)
    generate_figure_8_malicious_ratio(attack_csv, out_dir)
    generate_figure_9_sdsr_attack(attack_csv, out_dir)
    generate_figure_10_latency_vs_nodes(sc_csv, out_dir)
    generate_figure_11_energy_lifetime(bench_csv, out_dir)
    generate_figure_12_hypervolume_distribution(bench_csv, out_dir)
    generate_figure_13_ablation(abl_csv, out_dir)
    generate_figure_14_sensitivity(sens_csv, out_dir)
    generate_figure_15_runtime_evals(bench_csv, out_dir)
    generate_figure_16_scalability_dense(sc_csv, out_dir)
    print("All 16 scientific figures successfully generated from empirical logs!")

if __name__ == "__main__":
    generate_all_figures(root_dir, os.path.join(root_dir, "figures"))
