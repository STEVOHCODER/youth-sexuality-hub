import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gamma

# Define the x domain (start slightly above 0 to avoid 0^0 edge cases)
x = np.linspace(0.001, 1.5, 500)

# Function to compute the fractional derivative of x^k
def frac_deriv_power(x, k, alpha):
    return (gamma(k + 1) / gamma(k - alpha + 1)) * x**(k - alpha)

# Set up the figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Define the fractional orders (from 0 to 1) and color map
alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
colors = plt.cm.viridis(np.linspace(0, 0.9, len(alphas)))

# --- Subplot 1: f(x) = x ---
for a, c in zip(alphas, colors):
    y = frac_deriv_power(x, 1, a)
    ax1.plot(x, y, label=rf'$\alpha = {a}$', color=c, lw=2.5)

ax1.set_title(r"Fractional Derivatives of $f(x) = x$", fontsize=14, pad=15)
ax1.set_xlabel("$x$", fontsize=12)
ax1.set_ylabel(r"$D^\alpha x$", fontsize=12)
ax1.legend(title="Derivative Order", fontsize=10)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.set_xlim(0, 1.5)
ax1.set_ylim(0, 1.6)

# --- Subplot 2: f(x) = x^2 ---
for a, c in zip(alphas, colors):
    y = frac_deriv_power(x, 2, a)
    ax2.plot(x, y, label=rf'$\alpha = {a}$', color=c, lw=2.5)

ax2.set_title(r"Fractional Derivatives of $f(x) = x^2$", fontsize=14, pad=15)
ax2.set_xlabel("$x$", fontsize=12)
ax2.set_ylabel(r"$D^\alpha x^2$", fontsize=12)
ax2.legend(title="Derivative Order", fontsize=10)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.set_xlim(0, 1.5)
ax2.set_ylim(0, 2.5)

# Layout and styling
plt.suptitle("Visualizing Fractional Calculus: The Continuous Transition of Derivatives", fontsize=18, y=1.02)
plt.tight_layout()
plt.show()
