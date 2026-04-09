import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gamma

# Create the figure and subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Define the fractional orders we want to plot
# Transitioning from 0 (the function itself) to 1 (the first derivative)
alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
colors = plt.cm.viridis(np.linspace(0, 0.9, len(alphas)))

# ==========================================
# SUBPLOT 1: Fractional Derivatives of x^2
# ==========================================
# Avoid exactly 0 to prevent 0^negative issues if alpha > 2 (though here max alpha is 1)
x1 = np.linspace(0.001, 2, 500) 

for alpha, color in zip(alphas, colors):
    # D^alpha [x^2] = ( Gamma(3) / Gamma(3 - alpha) ) * x^(2 - alpha)
    # Note: Gamma(3) = 2! = 2
    y1 = (gamma(3) / gamma(3 - alpha)) * (x1**(2 - alpha))
    
    label = f'$\\alpha = {alpha}$'
    if alpha == 0.0: label += ' (Function: $x^2$)'
    if alpha == 1.0: label += ' ($1^{st}$ Deriv: $2x$)'
        
    ax1.plot(x1, y1, label=label, color=color, linewidth=2)

ax1.set_title('Fractional Derivatives of $f(x) = x^2$', fontsize=14)
ax1.set_xlabel('x', fontsize=12)
ax1.set_ylabel('$D^\\alpha x^2$', fontsize=12)
ax1.legend(loc='upper left')
ax1.grid(True, linestyle='--', alpha=0.7)

# ==========================================
# SUBPLOT 2: Fractional Derivatives of sin(x)
# ==========================================
x2 = np.linspace(0, 2 * np.pi, 500)

for alpha, color in zip(alphas, colors):
    # D^alpha [sin(x)] = sin(x + alpha * pi / 2)
    y2 = np.sin(x2 + alpha * np.pi / 2)
    
    label = f'$\\alpha = {alpha}$'
    if alpha == 0.0: label += ' (Function: $\\sin(x)$)'
    if alpha == 1.0: label += ' ($1^{st}$ Deriv: $\\cos(x)$)'
        
    ax2.plot(x2, y2, label=label, color=color, linewidth=2)

ax2.set_title('Fractional Derivatives of $f(x) = \sin(x)$', fontsize=14)
ax2.set_xlabel('x', fontsize=12)
ax2.set_ylabel('$D^\\alpha \sin(x)$', fontsize=12)
ax2.axhline(0, color='black', linewidth=1)
ax2.legend(loc='upper right')
ax2.grid(True, linestyle='--', alpha=0.7)

# Finalizing layout
plt.suptitle('Visualizing Fractional Calculus: The Continuous Transition to the 1st Derivative', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()
