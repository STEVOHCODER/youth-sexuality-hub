import numpy as np
import matplotlib.pyplot as plt

# Define the domain for x (using strictly positive values to avoid complex roots)
x = np.linspace(0, 2.5, 500)

# Calculate the values for different derivative orders (alpha)
# 1. Classical 0th derivative (the function itself)
y_0 = x 

# 2. Fractional 0.5th derivative (half-derivative)
y_half = (2 / np.sqrt(np.pi)) * np.sqrt(x)

# 3. Classical 1st derivative
y_1 = np.ones_like(x)

# Initialize the plot
plt.figure(figsize=(10, 6))

# Plot the curves
plt.plot(x, y_0, label=r'$\alpha = 0$: $D^0 x = x$ (Original Function)', color='#1f77b4', linestyle='--')
plt.plot(x, y_half, label=r'$\alpha = 1/2$: $D^{1/2} x = \frac{2}{\sqrt{\pi}} \sqrt{x}$ (Fractional)', color='#9467bd', linewidth=2.5)
plt.plot(x, y_1, label=r'$\alpha = 1$: $D^1 x = 1$ (First Derivative)', color='#d62728', linestyle='-.')

# Formatting the graph
plt.title('Bridging Classical Calculus with Fractional Calculus', fontsize=14, fontweight='bold')
plt.xlabel('x', fontsize=12)
plt.ylabel(r'$D^\alpha x$', fontsize=12)
plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)
plt.grid(color='gray', linestyle=':', linewidth=0.7, alpha=0.7)
plt.legend(fontsize=12, loc='upper left')

# Render the plot
plt.show()
