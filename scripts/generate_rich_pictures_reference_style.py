"""
scripts/generate_rich_pictures_reference_style.py
Generates large, high-contrast, crystal-clear Rich Picture diagrams
inspired directly by the reference images (clean iconography, numbered flows,
large bold typography, ample whitespace, high-level enterprise layout).

Outputs:
- figures/figure_1_architecture.png: HDBO-MPA Framework Architectural Overview
- figures/figure_17_practical_application.png: Practical Smart Healthcare Implementation
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, FancyArrowPatch, Wedge
import numpy as np

os.makedirs("figures", exist_ok=True)

# ----------------- REUSABLE ICON PRIMITIVES -----------------

def draw_step_badge(ax, x, y, num_str, radius=0.32, fc="#0F172A", ec="#FFFFFF", text_color="#FFFFFF"):
    """Draws a numbered step badge (e.g. 1, 2, 3...) like in the reference image."""
    c = Circle((x, y), radius, fc=fc, ec=ec, lw=2.0, zorder=10)
    ax.add_patch(c)
    ax.text(x, y, num_str, ha="center", va="center", color=text_color,
            fontsize=12, weight="bold", zorder=11)

def draw_car(ax, x, y, scale=1.0, color="#1E293B"):
    """Draws a clean vehicle icon matching Reference Image 1."""
    # Body
    ax.add_patch(FancyBboxPatch((x, y), 2.0*scale, 0.55*scale, boxstyle="round,pad=0.03,rounding_size=0.08",
                                fc=color, ec=color, lw=1, zorder=5))
    # Cabin / Roof
    pts = [[x+0.35*scale, y+0.55*scale], [x+0.65*scale, y+1.05*scale],
           [x+1.35*scale, y+1.05*scale], [x+1.65*scale, y+0.55*scale]]
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec=color, zorder=5))
    # Windshield glass (light fill)
    pts_w = [[x+0.45*scale, y+0.58*scale], [x+0.7*scale, y+0.98*scale],
             [x+1.3*scale, y+0.98*scale], [x+1.55*scale, y+0.58*scale]]
    ax.add_patch(Polygon(pts_w, closed=True, fc="#F8FAFC", ec=color, lw=1, zorder=6))
    # Wheels
    ax.add_patch(Circle((x+0.45*scale, y-0.05*scale), 0.22*scale, fc="#334155", ec="#0F172A", lw=2, zorder=7))
    ax.add_patch(Circle((x+0.45*scale, y-0.05*scale), 0.10*scale, fc="#FFFFFF", ec="none", zorder=8))
    ax.add_patch(Circle((x+1.55*scale, y-0.05*scale), 0.22*scale, fc="#334155", ec="#0F172A", lw=2, zorder=7))
    ax.add_patch(Circle((x+1.55*scale, y-0.05*scale), 0.10*scale, fc="#FFFFFF", ec="none", zorder=8))

def draw_ambulance(ax, x, y, scale=1.0, color="#0284C7"):
    """Draws an ambulance with medical cross matching real-world health SIoT."""
    # Box Van Body
    ax.add_patch(FancyBboxPatch((x, y), 2.2*scale, 1.1*scale, boxstyle="round,pad=0.03,rounding_size=0.1",
                                fc="#FFFFFF", ec=color, lw=2.5, zorder=5))
    # Cab window
    ax.add_patch(Rectangle((x+1.6*scale, y+0.55*scale), 0.5*scale, 0.45*scale,
                           fc="#BAE6FD", ec=color, lw=1.5, zorder=6))
    # Red Cross on side
    cx, cy = x + 0.85*scale, y + 0.60*scale
    cs = 0.22 * scale
    ax.add_patch(Rectangle((cx - cs*0.35, cy - cs), cs*0.7, cs*2, fc="#EF4444", ec="none", zorder=7))
    ax.add_patch(Rectangle((cx - cs, cy - cs*0.35), cs*2, cs*0.7, fc="#EF4444", ec="none", zorder=7))
    # Wheels
    ax.add_patch(Circle((x+0.5*scale, y-0.08*scale), 0.24*scale, fc="#1E293B", ec="#0F172A", lw=2, zorder=8))
    ax.add_patch(Circle((x+1.7*scale, y-0.08*scale), 0.24*scale, fc="#1E293B", ec="#0F172A", lw=2, zorder=8))

def draw_hospital(ax, x, y, w=2.4, h=2.8, color="#0369A1"):
    """Draws a multi-story building icon matching Reference Image 2."""
    ax.add_patch(Rectangle((x, y), w, h, fc="#FFFFFF", ec=color, lw=2.5, zorder=4))
    # Entrance doors
    ax.add_patch(Rectangle((x+w/2-0.3, y), 0.6, 0.8, fc="#F59E0B", ec=color, lw=1.5, zorder=5))
    # Windows grid
    for row in range(3):
        for col in range(4):
            wx = x + 0.25 + col * (w - 0.5) / 3.5
            wy = y + 1.1 + row * 0.5
            ax.add_patch(Rectangle((wx, wy), 0.28, 0.32, fc="#BAE6FD", ec=color, lw=1.0, zorder=5))
    # Emergency Red Cross on roof
    rx, ry = x + w/2, y + h + 0.25
    rs = 0.22
    ax.add_patch(Rectangle((rx - rs*0.35, ry - rs), rs*0.7, rs*2, fc="#EF4444", ec="none", zorder=6))
    ax.add_patch(Rectangle((rx - rs, ry - rs*0.35), rs*2, rs*0.7, fc="#EF4444", ec="none", zorder=6))

def draw_monitor_with_gears(ax, x, y, scale=1.0, color="#0F172A"):
    """Draws a computer monitor with gears icon matching Reference Image 1."""
    # Monitor screen
    ax.add_patch(FancyBboxPatch((x, y), 2.4*scale, 1.6*scale, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc="#FFFFFF", ec=color, lw=3.0, zorder=5))
    # Stand neck & base
    ax.add_patch(Rectangle((x+1.05*scale, y-0.45*scale), 0.3*scale, 0.45*scale, fc=color, ec="none", zorder=4))
    ax.add_patch(FancyBboxPatch((x+0.6*scale, y-0.55*scale), 1.2*scale, 0.15*scale,
                                boxstyle="round,pad=0.02,rounding_size=0.05", fc=color, ec="none", zorder=4))
    # Gears in center
    gx, gy = x + 1.2*scale, y + 0.8*scale
    ax.add_patch(Circle((gx, gy), 0.40*scale, fc="#F1F5F9", ec=color, lw=2.0, zorder=6))
    ax.add_patch(Circle((gx, gy), 0.18*scale, fc="#FFFFFF", ec=color, lw=2.0, zorder=7))
    for ang in range(0, 360, 45):
        rad = np.radians(ang)
        px = gx + 0.42*scale * np.cos(rad)
        py = gy + 0.42*scale * np.sin(rad)
        ax.add_patch(Circle((px, py), 0.08*scale, fc=color, ec="none", zorder=6))

def draw_database(ax, x, y, scale=1.0, color="#0F172A"):
    """Draws database cylinders matching Reference Image 1."""
    w, h = 1.4*scale, 0.4*scale
    for i in range(3):
        cy = y + i * 0.42*scale
        ax.add_patch(FancyBboxPatch((x, cy), w, h, boxstyle="round,pad=0.03,rounding_size=0.18",
                                    fc="#FFFFFF", ec=color, lw=2.2, zorder=5 + i))
        # Cylinder side lines
        ax.plot([x, x], [cy, cy + h], color=color, lw=2.2, zorder=6 + i)
        ax.plot([x + w, x + w], [cy, cy + h], color=color, lw=2.2, zorder=6 + i)

def draw_checkmark_circle(ax, x, y, radius=0.75, color="#16A34A"):
    """Draws a large green checkmark badge matching Reference Image 1."""
    ax.add_patch(Circle((x, y), radius, fc="#FFFFFF", ec=color, lw=4.0, zorder=5))
    # Thick checkmark
    pts = [[x - 0.35*radius, y - 0.05*radius],
           [x - 0.08*radius, y - 0.42*radius],
           [x + 0.48*radius, y + 0.42*radius]]
    ax.plot([pts[0][0], pts[1][0], pts[2][0]], [pts[0][1], pts[1][1], pts[2][1]],
            color=color, lw=5.5, solid_capstyle='round', solid_joinstyle='round', zorder=6)

def draw_alert_circle(ax, x, y, radius=0.75, color="#DC2626"):
    """Draws a large red exclamation mark badge matching Reference Image 1."""
    ax.add_patch(Circle((x, y), radius, fc="#FFFFFF", ec=color, lw=4.0, zorder=5))
    # Exclamation bar
    ax.plot([x, x], [y - 0.08*radius, y + 0.45*radius], color=color, lw=5.5, solid_capstyle='round', zorder=6)
    # Exclamation dot
    ax.add_patch(Circle((x, y - 0.38*radius), 0.10*radius, fc=color, ec="none", zorder=6))

def draw_human(ax, x, y, scale=1.0, color="#0F172A"):
    """Draws a clean human silhouette matching Reference Image 1."""
    # Head
    ax.add_patch(Circle((x, y + 0.85*scale), 0.32*scale, fc=color, ec="none", zorder=5))
    # Shoulders / Torso
    pts = [[x - 0.55*scale, y], [x + 0.55*scale, y],
           [x + 0.35*scale, y + 0.55*scale], [x - 0.35*scale, y + 0.55*scale]]
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec="none", zorder=5))

def draw_cloud(ax, x, y, w=2.6, h=1.4, color="#0284C7"):
    """Draws a cloud icon matching Reference Image 2."""
    ax.add_patch(Circle((x + 0.5*w/2.6, y + 0.5*h/1.4), 0.5*h, fc="#F0F9FF", ec=color, lw=2.0, zorder=4))
    ax.add_patch(Circle((x + 1.3*w/2.6, y + 0.8*h/1.4), 0.65*h, fc="#F0F9FF", ec=color, lw=2.0, zorder=4))
    ax.add_patch(Circle((x + 2.1*w/2.6, y + 0.5*h/1.4), 0.5*h, fc="#F0F9FF", ec=color, lw=2.0, zorder=4))
    ax.add_patch(Rectangle((x + 0.5*w/2.6, y), 1.6*w/2.6, 0.5*h, fc="#F0F9FF", ec="none", zorder=4))
    ax.plot([x + 0.5*w/2.6 - 0.35, x + 2.1*w/2.6 + 0.35], [y, y], color=color, lw=2.0, zorder=5)

def draw_annotated_arrow(ax, x1, y1, x2, y2, text="", step_num="", text_offset=(0, 0.25), color="#0F172A"):
    """Draws a directional arrow with large text and numbered badge matching Reference Image 1."""
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                            mutation_scale=18, fc=color, ec=color, lw=2.0, zorder=7)
    ax.add_patch(arrow)
    mx, my = (x1 + x2)/2.0, (y1 + y2)/2.0
    if step_num:
        draw_step_badge(ax, mx + text_offset[0]*0.4, my + text_offset[1]*0.7, step_num, radius=0.36)
    if text:
        ax.text(mx + text_offset[0], my + text_offset[1], text,
                ha="center", va="center", color=color, fontsize=11, weight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#E2E8F0", lw=1.0), zorder=9)


# ==============================================================================
# FIGURE 1: HDBO-MPA FRAMEWORK ARCHITECTURAL OVERVIEW (LARGE FULL-PAGE RICH PICTURE)
# ==============================================================================

def generate_figure_1_reference_style():
    """Generates Figure 1 following the reference images: layered enterprise layout,
    clean pictorial icons, large legible labels, numbered interaction flow."""
    fig, ax = plt.subplots(figsize=(20, 11), dpi=300)
    ax.axis('off')
    ax.set_xlim(-0.5, 20.5)
    ax.set_ylim(-0.5, 11.5)

    # Clean Pure White Canvas
    canvas = Rectangle((-0.4, -0.4), 20.8, 11.8, fc="#FFFFFF", ec="#0F172A", lw=2.5, zorder=0)
    ax.add_patch(canvas)

    # Header Title Banner
    ax.text(10.0, 10.9, "HDBO-MPA FRAMEWORK ARCHITECTURAL OVERVIEW",
            ha="center", va="center", fontsize=22, weight="bold", color="#0F172A")
    ax.text(10.0, 10.45, "Trust-Aware Multi-Objective Service Discovery in Social Internet of Things (Rich-Picture Systems Model)",
            ha="center", va="center", fontsize=13, style="italic", color="#475569")
    ax.plot([1.0, 19.0], [10.2, 10.2], color="#0F172A", lw=2.0)

    # ----------------- LAYER 1 (TOP): CLOUD & DECISION DOMAIN -----------------
    ax.text(1.2, 9.6, "LAYER 1: SERVICE APPLICATION & CLOUD TIER",
            ha="left", va="center", fontsize=14, weight="bold", color="#0369A1")
    
    # Cloud Applications Icon
    draw_cloud(ax, 3.0, 8.3, w=3.0, h=1.4, color="#0284C7")
    ax.text(4.5, 8.9, "Cloud Service Catalog\n& Data Center", ha="center", va="center",
            fontsize=12, weight="bold", color="#0369A1")

    # Central Terminal / Decision System (matching Reference Image 1)
    draw_monitor_with_gears(ax, 8.8, 8.1, scale=1.1, color="#0F172A")
    ax.text(10.1, 7.3, "TOPSIS MCDM Decision Core\n[Best Pareto Path P* Selected]",
            ha="center", va="center", fontsize=12, weight="bold", color="#0F172A")

    # Database Icon (matching Reference Image 1)
    draw_database(ax, 15.5, 8.1, scale=1.1, color="#0F172A")
    ax.text(16.3, 7.5, "Network & Trust\nGlobal Database", ha="center", va="center",
            fontsize=12, weight="bold", color="#0F172A")

    # Divider Line between Layer 1 & 2
    ax.plot([1.0, 19.0], [7.0, 7.0], color="#94A3B8", lw=1.5, ls="--")

    # ----------------- LAYER 2 (MIDDLE): EDGE GATEWAY & HDBO-MPA CORE -----------------
    ax.text(1.2, 6.6, "LAYER 2: HDBO-MPA CO-EVOLUTIONARY ENGINE & TRUST MATRIX",
            ha="left", va="center", fontsize=14, weight="bold", color="#047857")

    # Box A: Composite Trust Engine
    b_trust = FancyBboxPatch((1.2, 4.0), 5.4, 2.3, boxstyle="round,pad=0.08,rounding_size=0.15",
                             fc="#F0FDF4", ec="#059669", lw=2.5, zorder=3)
    ax.add_patch(b_trust)
    ax.text(3.9, 6.0, "Composite Trust Computation Engine", ha="center", va="center",
            fontsize=13, weight="bold", color="#065F46")
    ax.text(3.9, 5.4, "• Laplace Direct Trust: Sparse-sample smoothing\n• Shannon Entropy: Collusion recommender filtering\n• Median / MAD Filter: Robust 50% breakdown limit\n• Social Proximity: Multi-relational tie weight",
            ha="center", va="center", fontsize=11, color="#1E293B")

    # Box B: Dual Co-Evolutionary Swarm Core
    b_swarm = FancyBboxPatch((7.2, 4.0), 5.6, 2.3, boxstyle="round,pad=0.08,rounding_size=0.15",
                             fc="#FFFBEB", ec="#D97706", lw=2.5, zorder=3)
    ax.add_patch(b_swarm)
    ax.text(10.0, 6.0, "Co-Evolutionary Swarm Optimizer", ha="center", va="center",
            fontsize=13, weight="bold", color="#92400E")
    ax.text(10.0, 5.4, "• DBO Exploration (50%): Ball-rolling & breeding zones\n• MPA Exploitation (50%): Brownian & Lévy flights\n• FADs Effect: Stagnation jump perturbation\n• Shared External Non-Dominated Pareto Archive",
            ha="center", va="center", fontsize=11, color="#1E293B")

    # Box C: Graph-Constrained Priority Decoder
    b_decode = FancyBboxPatch((13.4, 4.0), 5.6, 2.3, boxstyle="round,pad=0.08,rounding_size=0.15",
                              fc="#FAF5FF", ec="#7E22CE", lw=2.5, zorder=3)
    ax.add_patch(b_decode)
    ax.text(16.2, 6.0, "Path Decoding & Feasibility (100%)", ha="center", va="center",
            fontsize=13, weight="bold", color="#6B21A8")
    ax.text(16.2, 5.4, "• Priority Vector Traversal: <0.50, 0.30, 0.20>\n• Wilson Loop-Erasure: Instantaneous cycle purging\n• Dijkstra Fallback: Dead-end connectivity repair\n• 100% Guaranteed Feasible Routing Paths",
            ha="center", va="center", fontsize=11, color="#1E293B")

    # Divider Line between Layer 2 & 3
    ax.plot([1.0, 19.0], [3.6, 3.6], color="#94A3B8", lw=1.5, ls="--")

    # ----------------- LAYER 3 (BOTTOM): PHYSICAL & SOCIAL IoT ENVIRONMENT -----------------
    ax.text(1.2, 3.2, "LAYER 3: DISTRIBUTED SOCIAL IoT FIELD & THREAT LANDSCAPE",
            ha="left", va="center", fontsize=14, weight="bold", color="#B91C1C")

    # Requester Node (Patient / Smart Vehicle)
    draw_car(ax, 1.4, 1.2, scale=1.2, color="#2563EB")
    ax.text(2.6, 0.5, "Requester Device (s)\n[Service Query Initiator]",
            ha="center", va="center", fontsize=12, weight="bold", color="#1E3A8A")

    # Intermediate Social Relay Nodes
    relays = [(6.2, 1.4, "Smart Gateway (u)", "#0D9488"),
              (9.8, 1.4, "Co-Work Relay (v)", "#7C3AED"),
              (13.4, 1.4, "Local Router (w)", "#EA580C")]
    for rx, ry, rname, rcol in relays:
        ax.add_patch(Circle((rx, ry + 0.3), 0.55, fc="#FFFFFF", ec=rcol, lw=3.0, zorder=5))
        ax.add_patch(Circle((rx, ry + 0.3), 0.22, fc=rcol, ec="none", zorder=6))
        ax.text(rx, ry - 0.45, rname, ha="center", va="center", fontsize=11, weight="bold", color=rcol)

    # Social Ties Links
    ax.plot([2.8, 5.6], [1.7, 1.7], color="#64748B", lw=2.5, ls=":")
    ax.text(4.2, 2.0, "POR Tie (0.90)", ha="center", va="center", fontsize=10, weight="bold", color="#475569")
    
    ax.plot([6.8, 9.2], [1.7, 1.7], color="#64748B", lw=2.5, ls=":")
    ax.text(8.0, 2.0, "CWR Tie (0.85)", ha="center", va="center", fontsize=10, weight="bold", color="#475569")

    ax.plot([10.4, 12.8], [1.7, 1.7], color="#64748B", lw=2.5, ls=":")
    ax.text(11.6, 2.0, "SOR Tie (0.65)", ha="center", va="center", fontsize=10, weight="bold", color="#475569")

    # Service Provider Node (Hospital / Server)
    draw_hospital(ax, 16.6, 0.7, w=2.4, h=2.2, color="#15803D")
    ax.text(17.8, 0.3, "Verified Service Provider (t)\n[Certified Diagnostic Server]",
            ha="center", va="center", fontsize=12, weight="bold", color="#166534")

    # Threat Warning Box (Adversary Collusion Ring)
    b_adv = FancyBboxPatch((8.0, 0.1), 4.2, 0.95, boxstyle="round,pad=0.04,rounding_size=0.1",
                           fc="#FEF2F2", ec="#EF4444", lw=2.0, zorder=4)
    ax.add_patch(b_adv)
    draw_alert_circle(ax, 8.4, 0.58, radius=0.28, color="#DC2626")
    ax.text(10.3, 0.58, "Adversary Threat Ring:\nBad-Mouthing & Collusion Blocked",
            ha="center", va="center", fontsize=10, weight="bold", color="#991B1B")

    # ----------------- NUMBERED INTERACTION ARROWS (1 to 7) -----------------
    # 1. Query submitted from Requester up to Trust Engine
    draw_annotated_arrow(ax, 2.4, 2.3, 3.2, 3.9, text="Submit Discovery Query R", step_num="1",
                         text_offset=(0, 0.25), color="#0284C7")

    # 2. Trust evaluation to Swarm Core
    draw_annotated_arrow(ax, 6.7, 5.15, 7.1, 5.15, text="Composite Trust T_comp", step_num="2",
                         text_offset=(0, 0.35), color="#059669")

    # 3. Swarm optimization to Priority Decoder
    draw_annotated_arrow(ax, 12.9, 5.15, 13.3, 5.15, text="Candidate Continuous Vector X", step_num="3",
                         text_offset=(0, 0.35), color="#D97706")

    # 4. Decoded non-dominated paths up to Decision Monitor
    draw_annotated_arrow(ax, 15.5, 6.4, 11.5, 8.1, text="Pareto Front A* to TOPSIS", step_num="4",
                         text_offset=(-0.3, 0.3), color="#7E22CE")

    # 5. Route verification with Global DB
    draw_annotated_arrow(ax, 11.4, 8.8, 15.3, 8.8, text="Verify Node Metadata", step_num="5",
                         text_offset=(0, 0.3), color="#0F172A")

    # 6. Selected optimal path deployed to Field Mesh
    draw_annotated_arrow(ax, 9.8, 7.6, 17.0, 3.1, text="Deploy Verified Route P*", step_num="6",
                         text_offset=(0.2, 0.3), color="#16A34A")

    plt.tight_layout()
    plt.savefig("figures/figure_1_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("figure_1_architecture.png regenerated in reference style.")


# ==============================================================================
# FIGURE 17: PRACTICAL REAL-WORLD SMART HEALTHCARE IMPLEMENTATION (RICH PICTURE)
# ==============================================================================

def generate_figure_17_reference_style():
    """Generates Figure 17 directly matching the workflow style of Reference Image 1
    (vehicles, terminal with gears, database, checkmark, alert, doctor/assistant, exit)."""
    fig, ax = plt.subplots(figsize=(20, 11), dpi=300)
    ax.axis('off')
    ax.set_xlim(-0.5, 20.5)
    ax.set_ylim(-0.5, 11.5)

    # Clean Pure White Canvas
    canvas = Rectangle((-0.4, -0.4), 20.8, 11.8, fc="#FFFFFF", ec="#0F172A", lw=2.5, zorder=0)
    ax.add_patch(canvas)

    # Header Title Banner
    ax.text(10.0, 10.9, "PRACTICAL IMPLEMENTATION: EMERGENCY SMART HEALTHCARE SIoT",
            ha="center", va="center", fontsize=22, weight="bold", color="#0F172A")
    ax.text(10.0, 10.45, "Real-Time Trust-Aware Telemedicine Service Discovery and Arrhythmia Diagnostic Workflow (Rich-Picture Model)",
            ha="center", va="center", fontsize=13, style="italic", color="#475569")
    ax.plot([1.0, 19.0], [10.2, 10.2], color="#0F172A", lw=2.0)

    # ----------------- ENTITIES MATCHING REFERENCE IMAGE 1 -----------------

    # 1. Left Side: Patient & Mobile Ambulance (Vehicles entering)
    draw_ambulance(ax, 1.2, 6.0, scale=1.3, color="#0284C7")
    ax.text(2.6, 5.3, "Emergency Ambulance\n[Mobile Telemedicine Unit]",
            ha="center", va="center", fontsize=12, weight="bold", color="#0369A1")

    # Wearable Cardiac Sensor on Patient
    ax.add_patch(FancyBboxPatch((1.2, 2.8), 2.8, 1.6, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc="#F0F9FF", ec="#0284C7", lw=2.0, zorder=4))
    ax.text(2.6, 3.9, "Patient Wearables (Requester s)", ha="center", va="center",
            fontsize=11, weight="bold", color="#0369A1")
    ax.text(2.6, 3.25, "• Continuous ECG Holter Monitor\n• Pulse Oximeter & SpO2\n• Cardiac Arrhythmia Detected!",
            ha="center", va="center", fontsize=9.5, color="#1E293B")

    # 2. Service Ticket / Discovery Request Token (matching ticket box in Image 1)
    ax.add_patch(FancyBboxPatch((5.6, 4.8), 2.2, 1.4, boxstyle="round,pad=0.03,rounding_size=0.08",
                                fc="#FFFFFF", ec="#0F172A", lw=2.2, zorder=4))
    ax.plot([5.8, 7.6], [5.9, 5.9], color="#0F172A", lw=1.5, ls="--")
    ax.text(6.7, 5.5, "EMERGENCY\nSERVICE QUERY", ha="center", va="center",
            fontsize=10, weight="bold", color="#0F172A")
    ax.text(6.7, 4.4, "Latency Limit <= 50 ms\nMin Trust >= 0.70", ha="center", va="center",
            fontsize=9.5, color="#475569")

    # 3. Center: Hospital Edge Gateway Terminal with Gears (matching computer in Image 1)
    draw_monitor_with_gears(ax, 9.2, 4.8, scale=1.2, color="#0F172A")
    ax.text(10.6, 4.0, "Hospital Edge Gateway\n[HDBO-MPA Optimization Engine]",
            ha="center", va="center", fontsize=12, weight="bold", color="#0F172A")

    # 4. Bottom Center: Hospital Electronic Health Database (matching cylinder in Image 1)
    draw_database(ax, 9.8, 1.0, scale=1.1, color="#0F172A")
    ax.text(10.6, 0.5, "EHR Patient Database\n& Historical Interaction Logs",
            ha="center", va="center", fontsize=11, weight="bold", color="#0F172A")

    # 5. Top Right: Verified ICU Specialist Provider (matching Successful Exit / Checkmark in Image 1)
    draw_hospital(ax, 14.8, 6.8, w=2.4, h=2.2, color="#15803D")
    ax.text(16.0, 6.4, "Certified ICU Arrhythmia AI\n[Provider Target t]",
            ha="center", va="center", fontsize=12, weight="bold", color="#166534")

    # Large Green Checkmark Circle (matching checkmark in Image 1)
    draw_checkmark_circle(ax, 18.5, 7.8, radius=0.75, color="#16A34A")
    ax.text(18.5, 6.7, "Telemetry Verified\nLatency: 42.8 ms (Pass)\nEnergy: 2.92 mJ",
            ha="center", va="center", fontsize=10.5, weight="bold", color="#15803D")

    # 6. Bottom Right: Alert / Malicious Compromised Node (matching exclamation mark in Image 1)
    draw_alert_circle(ax, 18.5, 3.2, radius=0.75, color="#DC2626")
    ax.text(18.5, 2.1, "Adversary Blocked\n• False Ratings Purged\n• Zero Slander Packets",
            ha="center", va="center", fontsize=10.5, weight="bold", color="#B91C1C")

    # 7. Bottom Right: Attending Cardiologist / Emergency Doctor (matching Assistant in Image 1)
    draw_human(ax, 14.8, 1.6, scale=1.1, color="#0F172A")
    ax.text(14.8, 1.1, "Attending Cardiologist\n[Clinical Intervention Initiated]",
            ha="center", va="center", fontsize=11, weight="bold", color="#0F172A")

    # ----------------- NUMBERED WORKFLOW ARROWS (1 to 12) MATCHING REFERENCE IMAGE 1 -----------------

    # 1. Patient generates arrhythmia signal to ambulance
    draw_annotated_arrow(ax, 2.6, 4.5, 2.6, 5.8, text="Vital ECG Stream", step_num="1",
                         text_offset=(-1.2, 0.0), color="#0284C7")

    # 2. Ambulance initiates request
    draw_annotated_arrow(ax, 4.1, 6.6, 5.6, 5.8, text="Generate Service Token", step_num="2",
                         text_offset=(0, 0.25), color="#0F172A")

    # 3. Input request to Edge Gateway
    draw_annotated_arrow(ax, 7.9, 5.5, 9.1, 5.5, text="Submit R to HDBO-MPA", step_num="3",
                         text_offset=(0, 0.25), color="#0F172A")

    # 4. Query Historical Logs from Database
    draw_annotated_arrow(ax, 10.3, 4.4, 10.3, 2.5, text="Fetch Interaction Logs", step_num="4",
                         text_offset=(-1.5, 0.0), color="#0F172A")

    # 5. Return Laplace Trust from Database
    draw_annotated_arrow(ax, 10.9, 2.5, 10.9, 4.4, text="Direct Trust Scores", step_num="5",
                         text_offset=(1.4, 0.0), color="#059669")

    # 6. Edge Gateway executes HDBO-MPA optimization
    ax.text(10.6, 6.5, "Co-Evolutionary Dual Swarms:\nDBO Scans + MPA Exploitation\nWilson Loop-Erasure (100% Feasible)",
            ha="center", va="center", fontsize=10, weight="bold", color="#D97706",
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFBEB", ec="#F59E0B", lw=1.2))

    # 7. Discovered route deployed to ICU provider
    draw_annotated_arrow(ax, 12.1, 5.8, 14.6, 7.4, text="Deploy Verified Route P*", step_num="7",
                         text_offset=(-0.2, 0.3), color="#16A34A")

    # 8. Checkmark verification
    draw_annotated_arrow(ax, 17.3, 7.8, 17.6, 7.8, text="SLA Satisfied", step_num="8",
                         text_offset=(0, 0.25), color="#16A34A")

    # 9. Adversary detection branch
    draw_annotated_arrow(ax, 12.1, 5.0, 17.6, 3.4, text="Detect Collusion Attempt", step_num="9",
                         text_offset=(0, -0.3), color="#DC2626")

    # 10. Alert sent to Attending Physician
    draw_annotated_arrow(ax, 18.5, 1.8, 16.2, 1.8, text="Telemetry Confirmed Safe", step_num="10",
                         text_offset=(0, -0.25), color="#0F172A")

    # 11. Cardiologist activates trauma bay
    draw_annotated_arrow(ax, 15.2, 3.0, 15.6, 6.6, text="Prepare Trauma Bay", step_num="11",
                         text_offset=(-1.4, 0.0), color="#15803D")

    plt.tight_layout()
    plt.savefig("figures/figure_17_practical_application.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("figure_17_practical_application.png regenerated in reference style.")

if __name__ == "__main__":
    generate_figure_1_reference_style()
    generate_figure_17_reference_style()
