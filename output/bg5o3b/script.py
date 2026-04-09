import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ==========================================
# 1. Setup the Figure
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Peridynamic Mathematical Model Visualizations", fontsize=16, fontweight='bold', y=0.98)

# ==========================================
# 2. Plot 1: The Peridynamic Horizon & Bonds
# ==========================================
# Generate random "material points" in a 2D domain
np.random.seed(42)
num_points = 200
points = np.random.rand(num_points, 2)

# Define the central point x and the horizon radius delta
center_x = np.array([0.5, 0.5])
delta = 0.25

# Draw the domain points
ax1.scatter(points[:, 0], points[:, 1], color='lightgray', s=15, zorder=1, label="Material Points")

# Draw the Horizon (Circle)
horizon = patches.Circle(center_x, delta, color='blue', alpha=0.1, zorder=2, label=r"Horizon $\mathcal{H}_{\mathbf{x}}$ ($\delta$)")
ax1.add_patch(horizon)
horizon_edge = patches.Circle(center_x, delta, color='blue', fill=False, linestyle='--', zorder=3)
ax1.add_patch(horizon_edge)

# Identify points within the horizon and draw "bonds"
inside_horizon = []
for p in points:
    dist = np.linalg.norm(p - center_x)
    if dist <= delta and dist > 0:
        inside_horizon.append(p)
        # Draw a bond (line) connecting x to x'
        ax1.plot([center_x[0], p[0]], [center_x[1], p[1]], color='royalblue', linewidth=0.8, alpha=0.6, zorder=4)

inside_horizon = np.array(inside_horizon)
# Highlight points interacting with x
if len(inside_horizon) > 0:
    ax1.scatter(inside_horizon[:, 0], inside_horizon[:, 1], color='dodgerblue', s=25, zorder=5, label=r"Interacting Points $\mathbf{x}'$")

# Plot the central point x
ax1.scatter(center_x[0], center_x[1], color='red', s=60, edgecolors='black', zorder=6, label=r"Central Point $\mathbf{x}$")

# Formatting Plot 1
ax1.set_aspect('equal')
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.set_title(r"Non-Local Interactions within Horizon $\delta$", fontsize=13)
ax1.set_xlabel("Spatial X-coordinate")
ax1.set_ylabel("Spatial Y-coordinate")
ax1.legend(loc='upper right', fontsize=9)


# ==========================================
# 3. Plot 2: Pairwise Force & Damage (PMB Model)
# ==========================================
# Prototypical Microelastic Brittle (PMB) force function
stretch = np.linspace(0, 0.05, 500)
critical_stretch = 0.02
micromodulus_c = 2500 # Constant 'c'

# Calculate Force: f(s) = c*s if s < s_critical, else 0
force = np.where(stretch <= critical_stretch, micromodulus_c * stretch, 0)

# Plot the force response
ax2.plot(stretch, force, color='crimson', linewidth=2.5, label=r"Pairwise Force $f(s)$")

# Highlight critical stretch
ax2.axvline(x=critical_stretch, color='black', linestyle='--', alpha=0.7, label=r"Critical Stretch ($s_0$)")

# Shade the area under the curve (Energy required to break the bond)
s_fill = np.linspace(0, critical_stretch, 100)
f_fill = micromodulus_c * s_fill
ax2.fill_between(s_fill, f_fill, color='crimson', alpha=0.15, label=r"Fracture Energy ($w_0$)")

# Formatting Plot 2
ax2.set_title("Bond Failure: Force vs. Stretch", fontsize=13)
ax2.set_xlabel(r"Bond Stretch ($s$)", fontsize=11)
ax2.set_ylabel(r"Pairwise Force Density ($f$)", fontsize=11)
ax2.set_xlim(0, 0.05)
ax2.set_ylim(0, max(force) * 1.2)
ax2.grid(True, linestyle=':', alpha=0.7)

# Annotate states
ax2.text(0.01, max(force)*0.5, 'Intact\n(Elastic Response)', horizontalalignment='center', fontsize=10, color='darkred')
ax2.text(0.035, max(force)*0.1, 'Broken\n(Irreversible Damage)', horizontalalignment='center', fontsize=10, color='gray')

ax2.legend(loc='upper right', fontsize=10)

# ==========================================
# 4. Render
# ==========================================
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.show()
