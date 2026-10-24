"""
scripts/generate_perfect_rich_diagrams.py
Generates large, high-contrast, publication-quality Rich Picture diagrams
faithfully adhering to the user's attached reference images:
- Clean, bold, iconic vector shapes (cars, ambulances, monitors with gears, database cylinders, checkmarks, alert badges, human figures, buildings).
- Large, bold, crystal-clear typography (14pt to 22pt) so text is never small.
- Numbered step-by-step workflow with arrows and numbered badges.
- Ample breathing room and whitespace.

Outputs:
- figures/figure_1_architecture.png: HDBO-MPA Architectural Overview Rich Picture
- figures/figure_17_practical_application.png: Practical Real-World Smart Healthcare Rich Picture
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, FancyArrowPatch, Wedge
import numpy as np

os.makedirs("figures", exist_ok=True)

# -------------------------------------------------------------
# ICON DRAWING ROUTINES (INSPIRED DIRECTLY BY REFERENCE IMAGES)
# -------------------------------------------------------------

def draw_step_badge(ax, x, y, num_str, radius=0.38, fc="#000000", text_color="#FFFFFF"):
    """Draws a numbered step badge (1, 2, 3...) matching Reference Image 1."""
    ax.add_patch(Circle((x, y), radius, fc=fc, ec="#000000", lw=1.5, zorder=12))
    ax.text(x, y, num_str, ha="center", va="center", color=text_color,
            fontsize=13, weight="bold", zorder=13)

def draw_car_icon(ax, x, y, scale=1.0, color="#000000"):
    """Draws a vehicle icon matching the car in Reference Image 1."""
    # Main lower body
    ax.add_patch(FancyBboxPatch((x, y), 2.2*scale, 0.6*scale,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                fc="#FFFFFF", ec=color, lw=3.0, zorder=5))
    # Cabin roof
    pts = [[x + 0.35*scale, y + 0.6*scale],
           [x + 0.65*scale, y + 1.15*scale],
           [x + 1.55*scale, y + 1.15*scale],
           [x + 1.85*scale, y + 0.6*scale]]
    ax.add_patch(Polygon(pts, closed=True, fc="#FFFFFF", ec=color, lw=3.0, zorder=5))
    # Windshield divide
    ax.plot([x + 1.05*scale, x + 1.05*scale], [y + 0.6*scale, y + 1.15*scale], color=color, lw=2.0, zorder=6)
    # Wheels
    ax.add_patch(Circle((x + 0.5*scale, y - 0.05*scale), 0.28*scale, fc="#000000", ec=color, lw=2.0, zorder=7))
    ax.add_patch(Circle((x + 0.5*scale, y - 0.05*scale), 0.12*scale, fc="#FFFFFF", ec="none", zorder=8))
    ax.add_patch(Circle((x + 1.7*scale, y - 0.05*scale), 0.28*scale, fc="#000000", ec=color, lw=2.0, zorder=7))
    ax.add_patch(Circle((x + 1.7*scale, y - 0.05*scale), 0.12*scale, fc="#FFFFFF", ec="none", zorder=8))

def draw_ambulance_icon(ax, x, y, scale=1.0, color="#0284C7"):
    """Draws an ambulance with medical cross."""
    # Box van body
    ax.add_patch(FancyBboxPatch((x, y), 2.5*scale, 1.2*scale,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                fc="#FFFFFF", ec=color, lw=3.0, zorder=5))
    # Front cab window
    ax.add_patch(Rectangle((x + 1.8*scale, y + 0.6*scale), 0.6*scale, 0.5*scale,
                           fc="#E0F2FE", ec=color, lw=2.0, zorder=6))
    # Red cross on side
    cx, cy = x + 0.95*scale, y + 0.65*scale
    cs = 0.25 * scale
    ax.add_patch(Rectangle((cx - cs*0.35, cy - cs), cs*0.7, cs*2, fc="#EF4444", ec="none", zorder=7))
    ax.add_patch(Rectangle((cx - cs, cy - cs*0.35), cs*2, cs*0.7, fc="#EF4444", ec="none", zorder=7))
    # Wheels
    ax.add_patch(Circle((x + 0.55*scale, y - 0.08*scale), 0.28*scale, fc="#0F172A", ec=color, lw=2.0, zorder=8))
    ax.add_patch(Circle((x + 1.95*scale, y - 0.08*scale), 0.28*scale, fc="#0F172A", ec=color, lw=2.0, zorder=8))

def draw_monitor_with_gears(ax, x, y, scale=1.0, color="#000000"):
    """Draws computer monitor with gear cogs matching 'Sistem' in Reference Image 1."""
    # Screen bezel
    ax.add_patch(FancyBboxPatch((x, y), 2.6*scale, 1.7*scale,
                                boxstyle="round,pad=0.04,rounding_size=0.15",
                                fc="#FFFFFF", ec=color, lw=3.5, zorder=5))
    # Display screen inset
    ax.add_patch(Rectangle((x + 0.15*scale, y + 0.15*scale), 2.3*scale, 1.4*scale,
                           fc="#F8FAFC", ec=color, lw=1.5, zorder=6))
    # Stand neck
    ax.add_patch(Rectangle((x + 1.15*scale, y - 0.45*scale), 0.3*scale, 0.45*scale,
                           fc=color, ec="none", zorder=4))
    # Stand base
    ax.add_patch(FancyBboxPatch((x + 0.7*scale, y - 0.55*scale), 1.2*scale, 0.15*scale,
                                boxstyle="round,pad=0.02,rounding_size=0.05",
                                fc=color, ec="none", zorder=4))
    # Gear 1 (Main center gear)
    g1x, g1y = x + 1.05*scale, y + 0.85*scale
    ax.add_patch(Circle((g1x, g1y), 0.38*scale, fc="#CBD5E1", ec=color, lw=2.0, zorder=7))
    ax.add_patch(Circle((g1x, g1y), 0.16*scale, fc="#FFFFFF", ec=color, lw=2.0, zorder=8))
    for ang in range(0, 360, 45):
        rad = np.radians(ang)
        px = g1x + 0.40*scale * np.cos(rad)
        py = g1y + 0.40*scale * np.sin(rad)
        ax.add_patch(Circle((px, py), 0.07*scale, fc=color, ec="none", zorder=7))
    # Gear 2 (Interlocking small gear)
    g2x, g2y = x + 1.6*scale, y + 1.05*scale
    ax.add_patch(Circle((g2x, g2y), 0.26*scale, fc="#94A3B8", ec=color, lw=2.0, zorder=7))
    ax.add_patch(Circle((g2x, g2y), 0.10*scale, fc="#FFFFFF", ec=color, lw=2.0, zorder=8))

def draw_database_icon(ax, x, y, scale=1.0, color="#000000"):
    """Draws database cylinders matching 'Database' in Reference Image 1."""
    w, h = 1.6*scale, 0.45*scale
    for i in range(3):
        cy = y + (2 - i) * 0.45*scale
        ax.add_patch(FancyBboxPatch((x, cy), w, h, boxstyle="round,pad=0.02,rounding_size=0.18",
                                    fc="#FFFFFF", ec=color, lw=2.8, zorder=5 + i))
        # Cylinder side vertical lines
        ax.plot([x, x], [cy, cy + h*0.9], color=color, lw=2.8, zorder=6 + i)
        ax.plot([x + w, x + w], [cy, cy + h*0.9], color=color, lw=2.8, zorder=6 + i)

def draw_checkmark_badge(ax, x, y, radius=0.9, color="#16A34A"):
    """Draws a large green checkmark badge in double circle matching Reference Image 1."""
    ax.add_patch(Circle((x, y), radius, fc="#FFFFFF", ec=color, lw=4.5, zorder=5))
    ax.add_patch(Circle((x, y), radius*0.88, fc="#F0FDF4", ec=color, lw=1.5, zorder=6))
    # Thick bold checkmark
    pts = [[x - 0.40*radius, y - 0.05*radius],
           [x - 0.10*radius, y - 0.45*radius],
           [x + 0.48*radius, y + 0.45*radius]]
    ax.plot([pts[0][0], pts[1][0], pts[2][0]], [pts[0][1], pts[1][1], pts[2][1]],
            color=color, lw=6.5, solid_capstyle='round', solid_joinstyle='round', zorder=7)

def draw_alert_badge(ax, x, y, radius=0.9, color="#DC2626"):
    """Draws a large red exclamation mark badge in double circle matching Reference Image 1."""
    ax.add_patch(Circle((x, y), radius, fc="#FFFFFF", ec=color, lw=4.5, zorder=5))
    ax.add_patch(Circle((x, y), radius*0.88, fc="#FEF2F2", ec=color, lw=1.5, zorder=6))
    # Exclamation bar
    ax.plot([x, x], [y - 0.08*radius, y + 0.50*radius], color=color, lw=7.0, solid_capstyle='round', zorder=7)
    # Exclamation dot
    ax.add_patch(Circle((x, y - 0.40*radius), 0.12*radius, fc=color, ec="none", zorder=7))

def draw_human_icon(ax, x, y, scale=1.0, color="#000000"):
    """Draws person silhouette matching 'Parking Assistant' in Reference Image 1."""
    # Head
    ax.add_patch(Circle((x, y + 0.85*scale), 0.36*scale, fc=color, ec="none", zorder=5))
    # Shoulders
    pts = [[x - 0.65*scale, y], [x + 0.65*scale, y],
           [x + 0.45*scale, y + 0.55*scale], [x - 0.45*scale, y + 0.55*scale]]
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec="none", zorder=5))

def draw_hospital_building(ax, x, y, w=2.6, h=2.8, color="#0369A1"):
    """Draws multi-story hospital building matching Reference Image 2."""
    ax.add_patch(Rectangle((x, y), w, h, fc="#FFFFFF", ec=color, lw=3.0, zorder=4))
    # Entrance
    ax.add_patch(Rectangle((x + w/2 - 0.35, y), 0.7, 0.85, fc="#F59E0B", ec=color, lw=2.0, zorder=5))
    # Windows
    for r in range(3):
        for c in range(3):
            wx = x + 0.3 + c * 0.75
            wy = y + 1.1 + r * 0.55
            ax.add_patch(Rectangle((wx, wy), 0.4, 0.35, fc="#BAE6FD", ec=color, lw=1.5, zorder=5))
    # Red cross on top
    rx, ry = x + w/2, y + h + 0.28
    rs = 0.26
    ax.add_patch(Rectangle((rx - rs*0.35, ry - rs), rs*0.7, rs*2, fc="#EF4444", ec="none", zorder=6))
    ax.add_patch(Rectangle((rx - rs, ry - rs*0.35), rs*2, rs*0.7, fc="#EF4444", ec="none", zorder=6))

def draw_cloud_icon(ax, x, y, w=3.0, h=1.5, color="#0284C7"):
    """Draws cloud icon matching Reference Image 2."""
    ax.add_patch(Circle((x + 0.6, y + 0.55), 0.55, fc="#F0F9FF", ec=color, lw=2.5, zorder=4))
    ax.add_patch(Circle((x + 1.5, y + 0.9), 0.75, fc="#F0F9FF", ec=color, lw=2.5, zorder=4))
    ax.add_patch(Circle((x + 2.4, y + 0.55), 0.55, fc="#F0F9FF", ec=color, lw=2.5, zorder=4))
    ax.add_patch(Rectangle((x + 0.6, y), 1.8, 0.65, fc="#F0F9FF", ec="none", zorder=4))
    ax.plot([x + 0.1, x + 2.9], [y, y], color=color, lw=2.5, zorder=5)

def draw_flow_arrow(ax, x1, y1, x2, y2, text="", step_num="", text_pos="above", color="#000000"):
    """Draws a bold arrow with numbered badge and large, bold text."""
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                            mutation_scale=22, fc=color, ec=color, lw=2.5, zorder=8)
    ax.add_patch(arrow)
    mx, my = (x1 + x2)/2.0, (y1 + y2)/2.0
    
    # Offset text above or below arrow
    offset_y = 0.35 if text_pos == "above" else -0.38
    
    if step_num:
        draw_step_badge(ax, mx - 1.2 if len(text) > 0 else mx, my + offset_y, step_num)
    if text:
        ax.text(mx + (0.3 if step_num else 0.0), my + offset_y, text,
                ha="center", va="center", color=color, fontsize=12.5, weight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#E2E8F0", lw=1.2), zorder=10)


# =====================================================================
# FIGURE 1: GENERAL ARCHITECTURAL OVERVIEW DIAGRAM (LARGE RICH PICTURE)
# =====================================================================

def generate_figure_1_clean_reference_style():
    """Generates Figure 1 matching Reference Images 1 and 2:
    Clean horizontal flow, large icons, large text, numbered steps."""
    fig, ax = plt.subplots(figsize=(15.5, 9.0), dpi=300)
    ax.axis('off')
    ax.set_xlim(-0.2, 15.5)
    ax.set_ylim(-0.2, 9.2)

    # Clean White Canvas
    ax.add_patch(Rectangle((-0.1, -0.1), 15.6, 9.3, fc="#FFFFFF", ec="#0F172A", lw=3.0, zorder=0))

    # Title
    ax.text(7.7, 8.6, "HDBO-MPA FRAMEWORK ARCHITECTURAL OVERVIEW",
            ha="center", va="center", fontsize=20, weight="bold", color="#0F172A")
    ax.text(7.7, 8.15, "Trust-Aware Multi-Objective Service Discovery in Social IoT (Rich-Picture Architecture)",
            ha="center", va="center", fontsize=13, style="italic", color="#475569")
    ax.plot([0.8, 14.6], [7.85, 7.85], color="#0F172A", lw=2.0)

    # 1. Left: Requester Vehicle (Matching Image 1 Car)
    draw_car_icon(ax, 0.8, 4.8, scale=1.1, color="#0F172A")
    ax.text(1.9, 4.3, "Requester Device (s)\n[Smart IoT Client]",
            ha="center", va="center", fontsize=13, weight="bold", color="#0F172A")

    # 2. Left-Center: Service Discovery Request Token (Matching Image 1 Ticket)
    ax.add_patch(FancyBboxPatch((3.8, 4.5), 2.2, 1.5, boxstyle="round,pad=0.04,rounding_size=0.1",
                                fc="#FFFFFF", ec="#0F172A", lw=2.8, zorder=5))
    ax.text(4.9, 5.4, "SERVICE QUERY", ha="center", va="center", fontsize=12, weight="bold", color="#0F172A")
    ax.plot([4.1, 5.7], [5.05, 5.05], color="#0F172A", lw=1.5, ls="--")
    ax.text(4.9, 4.75, "Latency <= 50 ms\nTrust >= 0.70", ha="center", va="center",
            fontsize=10.5, color="#334155")

    # 3. Center: HDBO-MPA Optimization Engine (Matching Image 1 Monitor with Gears)
    draw_monitor_with_gears(ax, 7.2, 4.3, scale=1.15, color="#0F172A")
    ax.text(8.7, 3.5, "HDBO-MPA System\n[Edge Gateway Engine]",
            ha="center", va="center", fontsize=14, weight="bold", color="#0F172A")

    # 4. Bottom-Center: Trust & Social Graph Database (Matching Image 1 Database)
    draw_database_icon(ax, 7.9, 0.8, scale=1.05, color="#0F172A")
    ax.text(8.7, 0.35, "Network & Trust Database",
            ha="center", va="center", fontsize=13, weight="bold", color="#0F172A")

    # 5. Top-Center: Cloud Applications Tier (Matching Image 2 Cloud)
    draw_cloud_icon(ax, 7.2, 6.2, w=2.8, h=1.3, color="#0284C7")
    ax.text(8.7, 6.75, "Cloud Service Catalog\n& Data Center",
            ha="center", va="center", fontsize=12, weight="bold", color="#0369A1")

    # 6. Right-Top: Successful Route Deployed Checkmark (Matching Image 1 Checkmark)
    draw_checkmark_badge(ax, 13.8, 6.2, radius=0.9, color="#16A34A")
    ax.text(13.8, 4.95, "100% Feasible Route Deployed\nLatency: 42.8 ms (3x Faster)\nEnergy: 2.92 mJ Conserved",
            ha="center", va="center", fontsize=11.5, weight="bold", color="#15803D")

    # 7. Right-Bottom: Collusion Adversary Alert (Matching Image 1 Exclamation)
    draw_alert_badge(ax, 13.8, 2.5, radius=0.9, color="#DC2626")
    ax.text(13.8, 1.25, "Adversary Collusion Blocked\n• Median/MAD Consensus\n• 50% Breakdown Security",
            ha="center", va="center", fontsize=11.5, weight="bold", color="#B91C1C")

    # ----------------- NUMBERED FLOW ARROWS (1 to 7) -----------------
    # Arrow 1: Car to Ticket
    draw_flow_arrow(ax, 2.2, 5.2, 3.7, 5.2, text="Initiate Query R", step_num="1", text_pos="above")

    # Arrow 2: Ticket to System
    draw_flow_arrow(ax, 6.1, 5.2, 7.1, 5.2, text="Submit Token", step_num="2", text_pos="above")

    # Arrow 3 & 4: System to Database
    draw_flow_arrow(ax, 8.2, 3.7, 8.2, 2.3, text="", step_num="3", text_pos="above")
    ax.text(7.2, 3.0, "Fetch Logs", fontsize=11, weight="bold", ha="right")

    draw_flow_arrow(ax, 9.2, 2.3, 9.2, 3.7, text="", step_num="4", text_pos="above")
    ax.text(10.2, 3.0, "Trust Matrix T_comp", fontsize=11, weight="bold", ha="left")

    # Arrow 5: System to Cloud
    draw_flow_arrow(ax, 8.7, 5.8, 8.7, 6.2, text="Verify Service", step_num="5", text_pos="above")

    # Arrow 6: System to Success Checkmark
    draw_flow_arrow(ax, 10.3, 5.4, 12.6, 6.2, text="Optimal Path P* Selected", step_num="6", text_pos="above", color="#16A34A")

    # Arrow 7: System to Alert
    draw_flow_arrow(ax, 10.3, 4.6, 12.6, 2.6, text="Filter Collusion Attacks", step_num="7", text_pos="above", color="#DC2626")

    plt.tight_layout()
    plt.savefig("figures/figure_1_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("figure_1_architecture.png generated with clean reference style.")


# ==============================================================================
# FIGURE 17: PRACTICAL REAL-WORLD SMART HEALTHCARE IMPLEMENTATION
# ==============================================================================

def generate_figure_17_clean_reference_style():
    """Generates Figure 17 faithfully reproducing the composition of Reference Image 1:
    Ambulance/patient on left -> Emergency ticket -> Central hospital gateway -> Database below ->
    ICU server & checkmark on right -> Alert on bottom right -> Attending doctor."""
    fig, ax = plt.subplots(figsize=(15.5, 9.0), dpi=300)
    ax.axis('off')
    ax.set_xlim(-0.2, 15.5)
    ax.set_ylim(-0.2, 9.2)

    # Clean White Canvas
    ax.add_patch(Rectangle((-0.1, -0.1), 15.6, 9.3, fc="#FFFFFF", ec="#0F172A", lw=3.0, zorder=0))

    # Title
    ax.text(7.7, 8.6, "EMERGENCY SMART HEALTHCARE SIoT DEPLOYMENT",
            ha="center", va="center", fontsize=20, weight="bold", color="#0F172A")
    ax.text(7.7, 8.15, "Real-World Practical Telemedicine Service Discovery and Arrhythmia Diagnostic Workflow (Rich-Picture Model)",
            ha="center", va="center", fontsize=13, style="italic", color="#475569")
    ax.plot([0.8, 14.6], [7.85, 7.85], color="#0F172A", lw=2.0)

    # 1. Left: Ambulance Mobile Unit (Matching Car in Image 1)
    draw_ambulance_icon(ax, 0.8, 5.6, scale=1.1, color="#0284C7")
    ax.text(2.1, 5.1, "Ambulance in Transit\n[Mobile Telemedicine Unit]",
            ha="center", va="center", fontsize=12.5, weight="bold", color="#0369A1")

    # Wearable ECG Monitor on Patient (Matching Image 1 input)
    ax.add_patch(FancyBboxPatch((0.8, 2.5), 2.6, 1.7, boxstyle="round,pad=0.04,rounding_size=0.1",
                                fc="#FFFFFF", ec="#0284C7", lw=2.5, zorder=5))
    ax.text(2.1, 3.8, "Patient Wearables (s)", ha="center", va="center", fontsize=12, weight="bold", color="#0369A1")
    ax.text(2.1, 3.1, "• 12-Lead ECG Holter\n• SpO2 Pulse Monitor\n• Arrhythmia Detected!",
            ha="center", va="center", fontsize=10.5, color="#1E293B")

    # 2. Emergency Discovery Ticket (Matching Ticket Box in Image 1)
    ax.add_patch(FancyBboxPatch((4.0, 4.3), 2.2, 1.5, boxstyle="round,pad=0.04,rounding_size=0.1",
                                fc="#FFFFFF", ec="#0F172A", lw=2.8, zorder=5))
    ax.text(5.1, 5.3, "EMERGENCY TICKET", ha="center", va="center", fontsize=11.5, weight="bold", color="#0F172A")
    ax.plot([4.3, 5.9], [4.95, 4.95], color="#0F172A", lw=1.5, ls="--")
    ax.text(5.1, 4.55, "Req: ICU Arrhythmia\nSLA: <= 50.0 ms", ha="center", va="center",
            fontsize=10.5, color="#334155")

    # 3. Center: Hospital Edge Gateway (Matching 'Sistem' Monitor in Image 1)
    draw_monitor_with_gears(ax, 7.3, 4.1, scale=1.15, color="#0F172A")
    ax.text(8.8, 3.3, "Hospital Edge Gateway\n[HDBO-MPA Engine]",
            ha="center", va="center", fontsize=14, weight="bold", color="#0F172A")

    # 4. Bottom Center: EHR Database (Matching Database in Image 1)
    draw_database_icon(ax, 8.0, 0.7, scale=1.05, color="#0F172A")
    ax.text(8.8, 0.25, "EHR Database & Logs",
            ha="center", va="center", fontsize=12.5, weight="bold", color="#0F172A")

    # 5. Right-Top: Checkmark Success Badge (Matching Image 1 Checkmark)
    draw_checkmark_badge(ax, 13.8, 6.2, radius=0.9, color="#16A34A")
    ax.text(13.8, 4.95, "Telemetry Verified!\nLatency: 42.8 ms (< 50 ms SLA)\nEnergy: 2.92 mJ (Battery Safe)",
            ha="center", va="center", fontsize=11.5, weight="bold", color="#15803D")

    # 6. Right-Bottom: Alert Badge (Matching Image 1 Exclamation)
    draw_alert_badge(ax, 13.8, 2.5, radius=0.9, color="#DC2626")
    ax.text(13.8, 1.25, "Collusion Blocked!\n• Fake Ratings Stripped\n• Zero Slander Accepted",
            ha="center", va="center", fontsize=11.5, weight="bold", color="#B91C1C")

    # 7. Doctor Avatar (Matching Parking Assistant in Image 1)
    draw_human_icon(ax, 11.4, 0.8, scale=0.9, color="#0F172A")
    ax.text(11.4, 0.35, "Attending Cardiologist\n[Trauma Bay Ready]",
            ha="center", va="center", fontsize=11, weight="bold", color="#0F172A")

    # ----------------- NUMBERED FLOW ARROWS (1 to 8) -----------------
    # Arrow 1: Wearable to Ambulance
    draw_flow_arrow(ax, 2.1, 4.3, 2.1, 5.5, text="Vital Stream", step_num="1", text_pos="above", color="#0284C7")

    # Arrow 2: Ambulance to Ticket
    draw_flow_arrow(ax, 2.5, 6.0, 3.9, 5.1, text="Gen Token", step_num="2", text_pos="above")

    # Arrow 3: Ticket to Gateway
    draw_flow_arrow(ax, 6.3, 5.0, 7.2, 5.0, text="Submit Query", step_num="3", text_pos="above")

    # Arrow 4 & 5: Gateway to Database
    draw_flow_arrow(ax, 8.3, 3.5, 8.3, 2.2, text="", step_num="4", text_pos="above")
    ax.text(7.3, 2.8, "Query Logs", fontsize=10.5, weight="bold", ha="right")

    draw_flow_arrow(ax, 9.3, 2.2, 9.3, 3.5, text="", step_num="5", text_pos="above")
    ax.text(10.3, 2.8, "Direct Trust", fontsize=10.5, weight="bold", ha="left")

    # Arrow 6: Gateway to Checkmark
    draw_flow_arrow(ax, 10.4, 5.2, 12.6, 6.2, text="Optimal Route P*", step_num="6", text_pos="above", color="#16A34A")

    # Arrow 7: Gateway to Alert
    draw_flow_arrow(ax, 10.4, 4.4, 12.6, 2.6, text="Isolate Attackers", step_num="7", text_pos="above", color="#DC2626")

    # Arrow 8: Gateway to Doctor
    draw_flow_arrow(ax, 9.8, 3.6, 11.0, 1.8, text="Alert ICU Team", step_num="8", text_pos="above")

    plt.tight_layout()
    plt.savefig("figures/figure_17_practical_application.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("figure_17_practical_application.png generated with clean reference style.")

if __name__ == "__main__":
    generate_figure_1_clean_reference_style()
    generate_figure_17_clean_reference_style()
