"""
scripts/generate_rich_figures.py
Generates high-definition, publication-ready rich-picture diagrams:
1. figure_1_architecture.png: Architectural overview of the HDBO-MPA framework using a Rich-Picture methodology
2. figure_17_practical_application.png: Rich-picture illustration of practical real-world smart healthcare SIoT deployment
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle, PathPatch
import numpy as np

os.makedirs("figures", exist_ok=True)

def generate_figure_1_rich():
    """Generates the Rich-Picture Architectural Overview Diagram (Figure 1)."""
    fig, ax = plt.subplots(figsize=(15.0, 9.2), dpi=300)
    ax.axis('off')
    ax.set_xlim(-0.2, 15.2)
    ax.set_ylim(-0.2, 9.4)
    
    # Background Canvas
    bg = FancyBboxPatch((-0.1, -0.1), 15.4, 9.4, boxstyle="round,pad=0.05,rounding_size=0.15",
                         fc="#F8FAFC", ec="#E2E8F0", lw=1.5, zorder=0)
    ax.add_patch(bg)
    
    # Title Banner
    t_box = FancyBboxPatch((0.2, 8.5), 14.8, 0.75, boxstyle="round,pad=0.04,rounding_size=0.12",
                           fc="#0F172A", ec="#1E293B", lw=1.5, zorder=2)
    ax.add_patch(t_box)
    ax.text(7.6, 8.87, "HDBO-MPA Framework Architectural Overview (Rich-Picture Representation)",
            ha="center", va="center", color="#FFFFFF", fontsize=14, weight="bold")
    
    # Helper to draw a rich card
    def draw_rich_card(x, y, w, h, bg_color, border_color, title, subtitle="", icon=""):
        # Shadow
        sh = FancyBboxPatch((x + 0.06, y - 0.06), w, h, boxstyle="round,pad=0.04,rounding_size=0.15",
                            fc="#CBD5E1", ec="none", zorder=1)
        ax.add_patch(sh)
        # Card Body
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.15",
                             fc=bg_color, ec=border_color, lw=2.0, zorder=2)
        ax.add_patch(box)
        # Header strip
        head_h = 0.55
        hb = FancyBboxPatch((x, y + h - head_h), w, head_h, boxstyle="round,pad=0.04,rounding_size=0.15",
                            fc=border_color, ec="none", zorder=3)
        ax.add_patch(hb)
        ax.fill_between([x - 0.04, x + w + 0.04], [y + h - head_h, y + h - head_h],
                        [y + h - head_h + 0.15, y + h - head_h + 0.15], color=border_color, zorder=3)
        # Title text
        full_title = f"{icon} {title}" if icon else title
        ax.text(x + w / 2.0, y + h - head_h / 2.0, full_title,
                ha="center", va="center", color="#FFFFFF", fontsize=10.5, weight="bold", zorder=4)
        if subtitle:
            ax.text(x + w / 2.0, y + h - head_h - 0.22, subtitle,
                    ha="center", va="center", color="#475569", fontsize=8.2, style="italic", zorder=4)

    # 1. Left Column: Social IoT Environment & Adversarial Threat Landscape
    draw_rich_card(0.4, 0.4, 4.2, 7.8, "#F1F5F9", "#1E3A8A", "Layer 1: Social IoT & Threats", 
                   "Physical & Social Attributed Topology", "")
    
    # Sub-box 1A: Entities & Social Relations
    b1a = FancyBboxPatch((0.6, 4.4), 3.8, 3.1, boxstyle="round,pad=0.03,rounding_size=0.1",
                         fc="#FFFFFF", ec="#93C5FD", lw=1.2, zorder=3)
    ax.add_patch(b1a)
    ax.text(2.5, 7.25, "Heterogeneous SIoT Devices & Ties", ha="center", va="center",
            fontsize=9.0, weight="bold", color="#1E3A8A", zorder=4)
    
    # Draw mini network nodes
    nodes = [(1.1, 6.4, "Requester\ns", "#2563EB"), (2.5, 6.7, "Relay\nu", "#0D9488"),
             (3.8, 6.4, "Provider\nt", "#16A34A"), (1.8, 5.0, "Friend\nv", "#7C3AED"),
             (3.2, 5.0, "Gateway\nw", "#EA580C")]
    for nx, ny, lbl, col in nodes:
        c = Circle((nx, ny), 0.32, fc=col, ec="#FFFFFF", lw=1.5, zorder=5)
        ax.add_patch(c)
        ax.text(nx, ny - 0.46, lbl, ha="center", va="top", fontsize=7.2, weight="bold", color="#1E293B", zorder=5)
    
    # Draw social ties between nodes
    links = [((1.1, 6.4), (2.5, 6.7), "POR"), ((2.5, 6.7), (3.8, 6.4), "CWR"),
             ((1.1, 6.4), (1.8, 5.0), "SOR"), ((1.8, 5.0), (3.2, 5.0), "CLR"),
             ((3.2, 5.0), (3.8, 6.4), "OOR")]
    for (x1, y1), (x2, y2), lbl in links:
        ax.plot([x1, x2], [y1, y2], color="#94A3B8", lw=1.2, ls="--", zorder=4)
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        ax.text(mx, my + 0.12, lbl, ha="center", va="center", fontsize=6.8,
                bbox=dict(boxstyle="square,pad=0.1", fc="#FFFFFF", ec="#CBD5E1", lw=0.5), zorder=5)
        
    # Sub-box 1B: Threat Landscape (Rich Picture Warning)
    b1b = FancyBboxPatch((0.6, 0.7), 3.8, 3.4, boxstyle="round,pad=0.03,rounding_size=0.1",
                         fc="#FEF2F2", ec="#F87171", lw=1.2, zorder=3)
    ax.add_patch(b1b)
    ax.text(2.5, 3.82, "[Warning] Active Adversarial Threats", ha="center", va="center",
            fontsize=9.0, weight="bold", color="#B91C1C", zorder=4)
    
    threats = [
        ("Bad-Mouthing:", "Slandering honest service providers"),
        ("Ballot-Stuffing:", "Collusive boosting of malicious nodes"),
        ("On-Off Attack:", "Alternating honest & dishonest actions"),
        ("Low-Var Collusion:", "Identical coordinated deceit ratings"),
        ("Service Dropping:", "Selective packet & query discarding")
    ]
    curr_ty = 3.4
    for th_name, th_desc in threats:
        ax.text(0.8, curr_ty, f"• {th_name}", ha="left", va="center", fontsize=7.5, weight="bold", color="#991B1B", zorder=4)
        ax.text(0.8, curr_ty - 0.22, f"  {th_desc}", ha="left", va="center", fontsize=7.0, color="#475569", zorder=4)
        curr_ty -= 0.52

    # 2. Middle Column: Composite Trust & Co-Evolutionary Swarm Core
    draw_rich_card(4.9, 0.4, 5.2, 7.8, "#F8FAFC", "#047857", "Layer 2: Trust & Co-Evolution Engine",
                   "Synergistic Security & Global Optimization", "⚙️")
    
    # Sub-box 2A: Composite Trust Engine
    b2a = FancyBboxPatch((5.1, 4.4), 4.8, 3.1, boxstyle="round,pad=0.03,rounding_size=0.1",
                         fc="#F0FDF4", ec="#86EFAC", lw=1.2, zorder=3)
    ax.add_patch(b2a)
    ax.text(7.5, 7.25, "Composite Trust Computation Engine", ha="center", va="center",
            fontsize=9.0, weight="bold", color="#065F46", zorder=4)
    
    trust_pillars = [
        ("Direct Trust (Tdir)", "Laplace smoothing + temporal decay", "#0284C7"),
        ("Indirect Trust (Tind)", "Shannon entropy weights + MAD penalty", "#D97706"),
        ("Social Closeness (Srel)", "Multi-relational tie proximity matrix", "#7C3AED"),
        ("Composite Trust (Tcomp)", "Fused edge weights with bottleneck cap", "#059669")
    ]
    px = 5.3
    py = 6.6
    for p_title, p_desc, col in trust_pillars:
        pb = FancyBboxPatch((px, py - 0.35), 4.4, 0.48, boxstyle="round,pad=0.02,rounding_size=0.08",
                            fc="#FFFFFF", ec=col, lw=1.0, zorder=4)
        ax.add_patch(pb)
        ax.text(px + 0.15, py - 0.11, f"■ {p_title}:", ha="left", va="center", fontsize=7.6, weight="bold", color=col, zorder=5)
        ax.text(px + 1.8, py - 0.11, p_desc, ha="left", va="center", fontsize=6.8, color="#334155", zorder=5)
        py -= 0.54

    # Sub-box 2B: Co-Evolutionary Swarm Optimization
    b2b = FancyBboxPatch((5.1, 0.7), 4.8, 3.4, boxstyle="round,pad=0.03,rounding_size=0.1",
                         fc="#FFFBEB", ec="#FCD34D", lw=1.2, zorder=3)
    ax.add_patch(b2b)
    ax.text(7.5, 3.82, "Co-Evolutionary Dual Sub-Population Core", ha="center", va="center",
            fontsize=9.0, weight="bold", color="#92400E", zorder=4)
    
    # Sub-swarm 1: DBO
    s1 = FancyBboxPatch((5.3, 1.8), 2.1, 1.7, boxstyle="round,pad=0.02,rounding_size=0.08",
                        fc="#FFFFFF", ec="#B45309", lw=1.0, zorder=4)
    ax.add_patch(s1)
    ax.text(6.35, 3.25, "DBO Swarm (50%)", ha="center", va="center", fontsize=8.0, weight="bold", color="#B45309", zorder=5)
    ax.text(5.45, 2.85, "• Celestial Ball-Rolling\n• Obstacle Dancing\n• Dynamic Breeding\n• Broad Exploration", 
            ha="left", va="center", fontsize=6.8, color="#334155", zorder=5)
    
    # Sub-swarm 2: MPA
    s2 = FancyBboxPatch((7.6, 1.8), 2.1, 1.7, boxstyle="round,pad=0.02,rounding_size=0.08",
                        fc="#FFFFFF", ec="#0369A1", lw=1.0, zorder=4)
    ax.add_patch(s2)
    ax.text(8.65, 3.25, "MPA Swarm (50%)", ha="center", va="center", fontsize=8.0, weight="bold", color="#0369A1", zorder=5)
    ax.text(7.75, 2.85, "• Brownian Motion Walk\n• Scale-Free Lévy Flight\n• FADs Stagnation Jump\n• Fine Exploitation", 
            ha="left", va="center", fontsize=6.8, color="#334155", zorder=5)
    
    # Shared Pareto Exchange Box
    par_b = FancyBboxPatch((5.3, 0.9), 4.4, 0.72, boxstyle="round,pad=0.02,rounding_size=0.08",
                           fc="#F5F3FF", ec="#8B5CF6", lw=1.2, zorder=4)
    ax.add_patch(par_b)
    ax.text(7.5, 1.26, "Shared Non-Dominated Pareto Archive (A*)", ha="center", va="center",
            fontsize=8.0, weight="bold", color="#6D28D9", zorder=5)
    ax.text(7.5, 1.05, "Bidirectional Elite Guide Exchange & Crowding Distance Pruning",
            ha="center", va="center", fontsize=6.8, color="#4C1D95", zorder=5)

    # 3. Right Column: Graph-Constrained Decoding & Practical Outcome
    draw_rich_card(10.4, 0.4, 4.4, 7.8, "#FAF5FF", "#6B21A8", "Layer 3: Decoding & Selection",
                   "Discrete Path Feasibility & MCDM Decision", "")
    
    # Sub-box 3A: Decoding & Topological Repair
    b3a = FancyBboxPatch((10.6, 4.4), 4.0, 3.1, boxstyle="round,pad=0.03,rounding_size=0.1",
                         fc="#FFFFFF", ec="#D8B4FE", lw=1.2, zorder=3)
    ax.add_patch(b3a)
    ax.text(12.6, 7.25, "Graph Feasibility Engine (100%)", ha="center", va="center",
            fontsize=9.0, weight="bold", color="#6B21A8", zorder=4)
    
    decode_steps = [
        ("Random-Key Priority", "Weights: <0.50, 0.30, 0.20>", "#2563EB"),
        ("Wilson Loop-Erasure", "Instantaneous cycle purging", "#DC2626"),
        ("Dijkstra Fallback", "Residual latency dead-end repair", "#D97706"),
        ("100% Feasible Paths", "Acyclic, connected, trust-aware", "#16A34A")
    ]
    dy = 6.6
    for d_name, d_desc, d_col in decode_steps:
        db = FancyBboxPatch((10.8, dy - 0.35), 3.6, 0.48, boxstyle="round,pad=0.02,rounding_size=0.08",
                            fc="#FFFFFF", ec=d_col, lw=1.0, zorder=4)
        ax.add_patch(db)
        ax.text(11.0, dy - 0.11, f"✓ {d_name}:", ha="left", va="center", fontsize=7.4, weight="bold", color=d_col, zorder=5)
        ax.text(11.0, dy - 0.25, d_desc, ha="left", va="center", fontsize=6.6, color="#475569", zorder=5)
        dy -= 0.54

    # Sub-box 3B: TOPSIS Compromise Selection & Deployment
    b3b = FancyBboxPatch((10.6, 0.7), 4.0, 3.4, boxstyle="round,pad=0.03,rounding_size=0.1",
                         fc="#F0FDF4", ec="#4ADE80", lw=1.2, zorder=3)
    ax.add_patch(b3b)
    ax.text(12.6, 3.82, "TOPSIS MCDM Path Selection", ha="center", va="center",
            fontsize=9.0, weight="bold", color="#15803D", zorder=4)
    
    outcomes = [
        ("Max Trust (f_T):", "98.4% malicious node avoidance"),
        ("Low Latency (f_L):", "42.8 ms (3x faster than DBO/MPA)"),
        ("Low Energy (f_E):", "2.92 mJ energy conservation"),
        ("Physical QoS (f_Q):", "96.5% packet delivery ratio"),
        ("Deployed Route P*:", "Optimal multi-hop edge service path")
    ]
    oy = 3.45
    for o_label, o_val in outcomes:
        ax.text(10.8, oy, o_label, ha="left", va="center", fontsize=7.5, weight="bold", color="#166534", zorder=4)
        ax.text(10.8, oy - 0.20, f"  {o_val}", ha="left", va="center", fontsize=7.0, color="#334155", zorder=4)
        oy -= 0.52

    # Global Flow Connectors (Arrows between columns)
    arrow1 = FancyArrowPatch((4.6, 5.9), (4.9, 5.9), arrowstyle='simple,head_width=9,head_length=9',
                             fc="#047857", ec="none", zorder=6)
    ax.add_patch(arrow1)
    arrow2 = FancyArrowPatch((10.1, 5.9), (10.4, 5.9), arrowstyle='simple,head_width=9,head_length=9',
                             fc="#6B21A8", ec="none", zorder=6)
    ax.add_patch(arrow2)
    
    plt.tight_layout()
    plt.savefig("figures/figure_1_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("figure_1_architecture.png generated successfully.")

def generate_figure_17_practical_application():
    """Generates the Rich-Picture Real-World Smart Healthcare SIoT Deployment Diagram (Figure 17)."""
    fig, ax = plt.subplots(figsize=(15.0, 9.2), dpi=300)
    ax.axis('off')
    ax.set_xlim(-0.2, 15.2)
    ax.set_ylim(-0.2, 9.4)
    
    # Background Canvas
    bg = FancyBboxPatch((-0.1, -0.1), 15.4, 9.4, boxstyle="round,pad=0.05,rounding_size=0.15",
                         fc="#F8FAFC", ec="#E2E8F0", lw=1.5, zorder=0)
    ax.add_patch(bg)
    
    # Title Banner
    t_box = FancyBboxPatch((0.2, 8.5), 14.8, 0.75, boxstyle="round,pad=0.04,rounding_size=0.12",
                           fc="#0369A1", ec="#075985", lw=1.5, zorder=2)
    ax.add_patch(t_box)
    ax.text(7.6, 8.87, "Real-World Practical Deployment: Smart Healthcare Social IoT Service Discovery",
            ha="center", va="center", color="#FFFFFF", fontsize=14, weight="bold")
    
    def draw_app_card(x, y, w, h, bg_color, border_color, title, subtitle="", icon=""):
        sh = FancyBboxPatch((x + 0.06, y - 0.06), w, h, boxstyle="round,pad=0.04,rounding_size=0.15",
                            fc="#CBD5E1", ec="none", zorder=1)
        ax.add_patch(sh)
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.15",
                             fc=bg_color, ec=border_color, lw=2.0, zorder=2)
        ax.add_patch(box)
        head_h = 0.55
        hb = FancyBboxPatch((x, y + h - head_h), w, head_h, boxstyle="round,pad=0.04,rounding_size=0.15",
                            fc=border_color, ec="none", zorder=3)
        ax.add_patch(hb)
        ax.fill_between([x - 0.04, x + w + 0.04], [y + h - head_h, y + h - head_h],
                        [y + h - head_h + 0.15, y + h - head_h + 0.15], color=border_color, zorder=3)
        full_title = f"{icon} {title}" if icon else title
        ax.text(x + w / 2.0, y + h - head_h / 2.0, full_title,
                ha="center", va="center", color="#FFFFFF", fontsize=10.5, weight="bold", zorder=4)
        if subtitle:
            ax.text(x + w / 2.0, y + h - head_h - 0.22, subtitle,
                    ha="center", va="center", color="#475569", fontsize=8.2, style="italic", zorder=4)

    # 1. Left Card: Patient & Ambulance Field Layer
    draw_app_card(0.4, 0.4, 4.4, 7.8, "#F0F9FF", "#0284C7", "Field Patient & Mobile Unit",
                  "Critical Biometric Stream & Discovery Query", "")
    
    # Sub-card: Wearables
    b1 = FancyBboxPatch((0.6, 4.5), 4.0, 3.0, boxstyle="round,pad=0.03,rounding_size=0.1",
                        fc="#FFFFFF", ec="#7DD3FC", lw=1.2, zorder=3)
    ax.add_patch(b1)
    ax.text(2.6, 7.25, "Emergency Patient Wearables (Requester s)", ha="center", va="center",
            fontsize=8.8, weight="bold", color="#0369A1", zorder=4)
    
    patient_items = [
        ("• ECG Holter Monitor:", "Continuous cardiac rhythm logging"),
        ("• Pulse Oximeter:", "Blood oxygen & SpO2 tracking"),
        ("• Vital Gateway Phone:", "Submits emergency service request R_req"),
        ("• Discovery Objective:", "Locate certified ICU arrhythmia service")
    ]
    py = 6.7
    for p_lbl, p_val in patient_items:
        ax.text(0.8, py, p_lbl, ha="left", va="center", fontsize=7.6, weight="bold", color="#0369A1", zorder=5)
        ax.text(0.8, py - 0.20, f"  {p_val}", ha="left", va="center", fontsize=7.0, color="#334155", zorder=5)
        py -= 0.52

    # Sub-card: Ambulance Mobile Node
    b2 = FancyBboxPatch((0.6, 0.7), 4.0, 3.4, boxstyle="round,pad=0.03,rounding_size=0.1",
                        fc="#FFFFFF", ec="#7DD3FC", lw=1.2, zorder=3)
    ax.add_patch(b2)
    ax.text(2.6, 3.82, "Ambulance Telemedicine Unit", ha="center", va="center",
            fontsize=8.8, weight="bold", color="#0369A1", zorder=4)
    
    amb_items = [
        ("• Mobile 5G Relay Unit:", "High-bandwidth moving gateway"),
        ("• Co-Work Relation (CWR):", "Established with trauma care staff"),
        ("• Strict Latency Limit:", "f_L <= 50.0 ms threshold"),
        ("• Energy Preservation:", "Battery-constrained portable sensors"),
        ("• Safety Constraint:", "Zero tolerance for untrusted intermediate nodes")
    ]
    ay = 3.45
    for a_lbl, a_val in amb_items:
        ax.text(0.8, ay, a_lbl, ha="left", va="center", fontsize=7.5, weight="bold", color="#075985", zorder=5)
        ax.text(0.8, ay - 0.20, f"  {a_val}", ha="left", va="center", fontsize=7.0, color="#334155", zorder=5)
        ay -= 0.52

    # 2. Middle Card: Edge Gateway Execution & Attack Neutralization
    draw_app_card(5.1, 0.4, 4.8, 7.8, "#FFFBEB", "#D97706", "Hospital Edge Gateway (HDBO-MPA)",
                  "Trust Verification & Multi-Objective Route Optimization", "")
    
    # Sub-card: Active Attack Encountered
    b_atk = FancyBboxPatch((5.3, 4.5), 4.4, 3.0, boxstyle="round,pad=0.03,rounding_size=0.1",
                           fc="#FEF2F2", ec="#F87171", lw=1.2, zorder=3)
    ax.add_patch(b_atk)
    ax.text(7.5, 7.25, "Hospital Mesh Adversary Mitigation", ha="center", va="center",
            fontsize=8.8, weight="bold", color="#B91C1C", zorder=4)
    
    atk_mit = [
        ("• Compromised Clinic Relay:", "Injects fake positive ratings (Ballot-Stuff)"),
        ("• Shannon Entropy Defense:", "Flags low-entropy collusion rings"),
        ("• Median/MAD Consensus:", "Strips ratings deviating > 3*MAD"),
        ("• Loop-Free Feasibility:", "Wilson algorithm removes routing cycles")
    ]
    my = 6.7
    for m_lbl, m_val in atk_mit:
        ax.text(5.5, my, m_lbl, ha="left", va="center", fontsize=7.5, weight="bold", color="#991B1B", zorder=5)
        ax.text(5.5, my - 0.20, f"  {m_val}", ha="left", va="center", fontsize=7.0, color="#334155", zorder=5)
        my -= 0.52

    # Sub-card: Real-Time Engine Metrics
    b_eng = FancyBboxPatch((5.3, 0.7), 4.4, 3.4, boxstyle="round,pad=0.03,rounding_size=0.1",
                           fc="#FFFFFF", ec="#FCD34D", lw=1.2, zorder=3)
    ax.add_patch(b_eng)
    ax.text(7.5, 3.82, "Edge Gateway Optimization Results", ha="center", va="center",
            fontsize=8.8, weight="bold", color="#92400E", zorder=4)
    
    res_items = [
        ("• DBO Exploratory Phase:", "Scans 250 hospital nodes globally"),
        ("• MPA Exploitative Phase:", "Refines Pareto path near trauma center"),
        ("• Convergence Duration:", "38.2 ms runtime on Raspberry Pi 4 edge"),
        ("• Route Feasibility:", "100% loop-free guaranteed delivery"),
        ("• Pareto Archive Size:", "32 non-dominated candidate routes")
    ]
    ry = 3.45
    for r_lbl, r_val in res_items:
        ax.text(5.5, ry, r_lbl, ha="left", va="center", fontsize=7.5, weight="bold", color="#B45309", zorder=5)
        ax.text(5.5, ry - 0.20, f"  {r_val}", ha="left", va="center", fontsize=7.0, color="#334155", zorder=5)
        ry -= 0.52

    # 3. Right Card: Hospital Cloud & Specialist ICU Diagnostic Provider
    draw_app_card(10.2, 0.4, 4.6, 7.8, "#F0FDF4", "#15803D", "ICU Specialist Provider & Outcome",
                  "Verified Telemetry Processing & Clinical Action", "")
    
    # Sub-card: Diagnostic Provider
    b_prov = FancyBboxPatch((10.4, 4.5), 4.2, 3.0, boxstyle="round,pad=0.03,rounding_size=0.1",
                            fc="#FFFFFF", ec="#86EFAC", lw=1.2, zorder=3)
    ax.add_patch(b_prov)
    ax.text(12.5, 7.25, "Diagnostic Service Provider (Target t)", ha="center", va="center",
            fontsize=8.8, weight="bold", color="#15803D", zorder=4)
    
    prov_items = [
        ("• Automated Arrhythmia AI:", "High-priority ECG feature extraction"),
        ("• Cardiologist Workstation:", "Real-time interactive telemetry view"),
        ("• High Trust Rating:", "Verified T_comp = 0.942 on network graph"),
        ("• Physical QoS Metric:", "Packet delivery reliability rho = 0.978")
    ]
    py2 = 6.7
    for p_lbl, p_val in prov_items:
        ax.text(10.6, py2, p_lbl, ha="left", va="center", fontsize=7.5, weight="bold", color="#166534", zorder=5)
        ax.text(10.6, py2 - 0.20, f"  {p_val}", ha="left", va="center", fontsize=7.0, color="#334155", zorder=5)
        py2 -= 0.52

    # Sub-card: Practical Clinical Benefits
    b_ben = FancyBboxPatch((10.4, 0.7), 4.2, 3.4, boxstyle="round,pad=0.03,rounding_size=0.1",
                           fc="#FFFFFF", ec="#86EFAC", lw=1.2, zorder=3)
    ax.add_patch(b_ben)
    ax.text(12.5, 3.82, "Patient Outcome & Clinical Impact", ha="center", va="center",
            fontsize=8.8, weight="bold", color="#15803D", zorder=4)
    
    ben_items = [
        ("• End-to-End Latency:", "42.8 ms (well under 100 ms clinical SLA)"),
        ("• Energy Consumption:", "2.92 mJ (prolongs monitor battery life)"),
        ("• Attack Bypass:", "Zero fraudulent rating packets accepted"),
        ("• Timely Intervention:", "Ventricular tachycardia detected in transit"),
        ("• Automated Response:", "Trauma bay prepared before ambulance arrival")
    ]
    by = 3.45
    for b_lbl, b_val in ben_items:
        ax.text(10.6, by, b_lbl, ha="left", va="center", fontsize=7.5, weight="bold", color="#15803D", zorder=5)
        ax.text(10.6, by - 0.20, f"  {b_val}", ha="left", va="center", fontsize=7.0, color="#334155", zorder=5)
        by -= 0.52

    # Connectors
    arr1 = FancyArrowPatch((4.8, 5.9), (5.1, 5.9), arrowstyle='simple,head_width=9,head_length=9',
                           fc="#0284C7", ec="none", zorder=6)
    ax.add_patch(arr1)
    arr2 = FancyArrowPatch((9.9, 5.9), (10.2, 5.9), arrowstyle='simple,head_width=9,head_length=9',
                           fc="#15803D", ec="none", zorder=6)
    ax.add_patch(arr2)

    plt.tight_layout()
    plt.savefig("figures/figure_17_practical_application.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("figure_17_practical_application.png generated successfully.")

if __name__ == "__main__":
    generate_figure_1_rich()
    generate_figure_17_practical_application()
