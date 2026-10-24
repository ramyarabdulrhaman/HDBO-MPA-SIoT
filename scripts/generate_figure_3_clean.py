"""
Script: generate_figure_3_clean.py
Generates a crystal-clear, publication-quality Figure 3 flowchart for HDBO-MPA without any overlapping text.
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def create_figure_3(output_path):
    fig, ax = plt.subplots(figsize=(13.6, 7.4), dpi=300)
    ax.axis('off')
    
    # Background coordinate space
    ax.set_xlim(-0.3, 13.5)
    ax.set_ylim(-0.4, 7.4)
    
    # Color palette
    c_blue = {'bg': '#F1F5F9', 'border': '#1E3A8A', 'head': '#1E3A8A'}
    c_amber = {'bg': '#FFFBEB', 'border': '#B45309', 'head': '#92400E'}
    c_green = {'bg': '#F0FDF4', 'border': '#15803D', 'head': '#166534'}
    c_purple = {'bg': '#FAF5FF', 'border': '#7E22CE', 'head': '#6B21A8'}
    c_teal = {'bg': '#F0FDFA', 'border': '#0F766E', 'head': '#115E59'}

    def draw_card(x, y, w, h, c_dict, title, items):
        # Drop shadow
        shadow = FancyBboxPatch((x + 0.05, y - 0.05), w, h, boxstyle="round,pad=0.06,rounding_size=0.15",
                                fc='#CBD5E1', ec='none', zorder=1)
        ax.add_patch(shadow)
        
        # Main card box
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.15",
                              fc=c_dict['bg'], ec=c_dict['border'], lw=1.8, zorder=2)
        ax.add_patch(rect)
        
        # Header banner
        h_h = 0.52
        banner = FancyBboxPatch((x, y + h - h_h), w, h_h, boxstyle="round,pad=0.06,rounding_size=0.15",
                                fc=c_dict['border'], ec='none', zorder=3)
        ax.add_patch(banner)
        # square bottom of banner
        ax.fill_between([x - 0.06, x + w + 0.06], [y + h - h_h, y + h - h_h], [y + h - h_h + 0.15, y + h - h_h + 0.15],
                        color=c_dict['border'], zorder=3)
        
        # Title text
        ax.text(x + w/2.0, y + h - h_h/2.0, title, ha='center', va='center',
                weight='bold', fontsize=9.5, color='white', zorder=4)
        
        # Content bullets
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

    # Cards Placement (cards top at y = 5.6 to leave y in [5.7, 7.3] completely free for top feedback loop)
    # 1. STAGE 1: Swarm Initialization
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

    # 2A. STAGE 2A: DBO Operator Execution (Top Center)
    s2a_items = [
        "### Global Exploration Operators",
        "• Ball-Rolling (p = 0.30): Celestial navigation",
        "• Obstacle Dancing: θ ∈ (0, π] reorientation",
        "• Dynamic Breeding: Spatially bounded zone",
        "• Stealing Regimes: Foraging across best food"
    ]
    draw_card(3.1, 3.2, 3.4, 2.4, c_amber, "STAGE 2A: DBO EXPLORATION", s2a_items)

    # 2B. STAGE 2B: MPA Operator Execution (Bottom Center)
    s2b_items = [
        "### Multi-Regime Exploitation",
        "• Phase 1 (t < T_max/3): High velocity Brownian",
        "• Phase 2 (T/3 ≤ t < 2T/3): Mixed Lévy + Brownian",
        "• Phase 3 (t ≥ 2T_max/3): Scale-free Lévy flights",
        "• FADs Perturbation: Triggers if HV stalls ≥ 3 iters"
    ]
    draw_card(3.1, 0.2, 3.4, 2.4, c_green, "STAGE 2B: MPA EXPLOITATION", s2b_items)

    # Co-Evolution Exchange Badge between 2A and 2B
    badge = FancyBboxPatch((3.7, 2.68), 2.2, 0.42, boxstyle="round,pad=0.04,rounding_size=0.1",
                           fc='#EFF6FF', ec='#2563EB', lw=1.2, zorder=5)
    ax.add_patch(badge)
    ax.text(4.8, 2.89, "⇄ Co-Evolution & Elite Exchange", ha='center', va='center',
            weight='bold', fontsize=7.5, color='#1D4ED8', zorder=6)

    # 3. STAGE 3: Combinatorial Graph Decoding & Loop Erasure
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

    # 4. STAGE 4: Multi-Objective Archive & Decision Making
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

    # ARROWS & CONNECTORS
    arrow_props = dict(facecolor='#1E293B', edgecolor='#1E293B', width=1.8, headwidth=6.0, headlength=6.5, zorder=5)
    
    # From Stage 1 to 2A and 2B
    ax.annotate('', xy=(3.05, 4.4), xytext=(2.55, 3.8), arrowprops=arrow_props)
    ax.text(2.60, 4.45, "N_dbo", fontsize=7.6, weight='bold', color='#B45309', zorder=6)
    
    ax.annotate('', xy=(3.05, 1.4), xytext=(2.55, 2.0), arrowprops=arrow_props)
    ax.text(2.60, 1.30, "N_mpa", fontsize=7.6, weight='bold', color='#15803D', zorder=6)

    # From Stage 2A & 2B to Stage 3
    ax.annotate('', xy=(7.05, 3.9), xytext=(6.55, 4.4), arrowprops=arrow_props)
    ax.annotate('', xy=(7.05, 2.0), xytext=(6.55, 1.4), arrowprops=arrow_props)

    # From Stage 3 to Stage 4
    ax.annotate('', xy=(10.45, 2.9), xytext=(9.95, 2.9), arrowprops=arrow_props)
    ax.text(10.2, 3.12, "Routes", ha='center', fontsize=7.2, weight='bold', color='#475569')

    # FEEDBACK LOOP: Clean routing with badge in the middle
    # Right segment: from Stage 4 top (11.8, 5.6) -> up to 6.55 -> to right edge of badge (10.0, 6.55)
    ax.plot([11.8, 11.8, 10.1], [5.6, 6.55, 6.55], color='#DC2626', lw=2.0, zorder=7)
    # Left segment: from left edge of badge (6.5, 6.55) -> left to 4.8 -> down to Stage 2A (4.8, 5.65)
    ax.plot([6.5, 4.8, 4.8], [6.55, 6.55, 5.65], color='#DC2626', lw=2.0, zorder=7)
    
    # Arrow head at Stage 2A
    ax.annotate('', xy=(4.8, 5.62), xytext=(4.8, 5.75),
                arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=2.0, headwidth=6.5, headlength=6.0, zorder=8))
    
    # Feedback badge centered between x=6.5 and 10.1 (width 3.6, height 0.46)
    f_box = FancyBboxPatch((6.5, 6.32), 3.6, 0.46, boxstyle="round,pad=0.04,rounding_size=0.1",
                           fc='#FEF2F2', ec='#DC2626', lw=1.5, zorder=9)
    ax.add_patch(f_box)
    ax.text(8.3, 6.55, "Elite Guide X_best Feedback Loop (t = 1 ... T_max)",
            ha='center', va='center', weight='bold', fontsize=7.8, color='#991B1B', zorder=10)

    # FINAL OUTPUT ARROW: Bottom of Stage 4
    ax.annotate('', xy=(11.8, -0.32), xytext=(11.8, 0.15),
                arrowprops=dict(facecolor='#0F766E', edgecolor='#0F766E', width=2.6, headwidth=7.5, zorder=7))
    out_box = FancyBboxPatch((10.3, -0.36), 3.0, 0.42, boxstyle="round,pad=0.04,rounding_size=0.1",
                            fc='#0F766E', ec='none', zorder=8)
    ax.add_patch(out_box)
    ax.text(11.8, -0.15, "Optimal Operational Route P*", ha='center', va='center',
            weight='bold', fontsize=8.5, color='white', zorder=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated clean Figure 3 at: {output_path}")

if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(__file__), "..", "figures")
    out_file = os.path.join(out_dir, "figure_3_workflow.png")
    create_figure_3(out_file)
