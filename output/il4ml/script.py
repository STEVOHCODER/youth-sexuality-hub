# filename: script.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import gamma
import math

def generate_fractional_calculus_data():
    """
    Generates a dataset based on the Riemann-Liouville fractional derivative 
    formula for polynomials derived in the text:
    D^alpha x^n = Gamma(n + 1) / Gamma(n - alpha + 1) * x^(n - alpha)
    """
    data = []
    x_discrete_values = [1, 2, 3, 4, 5]
    n_degrees = [1, 2, 3] # x^1, x^2, x^3
    alpha_orders = [0.0, 0.3333, 0.5, 1.0, 2.0] # 0 (identity), 1/3, 1/2, 1 (first deriv), 2 (second deriv)

    for n in n_degrees:
        for alpha in alpha_orders:
            # Skip invalid classical derivatives (e.g., 2nd derivative of x^1 annihilates to 0)
            if n - alpha < 0 and alpha.is_integer():
                coeff = 0
            else:
                coeff = gamma(n + 1) / gamma(n - alpha + 1)
                
            for x in x_discrete_values:
                if coeff == 0:
                    val = 0
                else:
                    val = coeff * (x ** (n - alpha))
                
                data.append({
                    "x_value": x,
                    "Polynomial_Degree_n": n,
                    "Derivative_Order_alpha": round(alpha, 4),
                    "Coefficient": coeff,
                    "Computed_Value": val
                })
                
    return pd.DataFrame(data)

def create_pivot_and_export(df, output_excel="fractional_calculus_analysis.xlsx"):
    """
    Pivots the dataset to show the average computed values by Degree and Order,
    and exports both raw and pivoted data to Excel with formatting.
    """
    # Create Pivot Table: Average computed value for each Polynomial Degree across Derivative Orders
    pivot_df = pd.pivot_table(
        df,
        values='Computed_Value',
        index=['Polynomial_Degree_n', 'x_value'],
        columns=['Derivative_Order_alpha'],
        aggfunc='mean'
    )
    
    # Export to Excel
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Raw_Derivatives_Data', index=False)
        pivot_df.to_excel(writer, sheet_name='Pivot_Analysis')
        
    print(f"Data and Pivot tables successfully exported to {output_excel}")
    return pivot_df

def plot_fractional_graphs():
    """
    Plots the Gamma function values (Table 2.2) and the fractional 
    derivative curves of polynomials (Examples 1-4).
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # --- GRAPH 1: The Gamma Function & Table 2.2 Values ---
    z_vals = np.linspace(0.1, 5.5, 500)
    gamma_z = gamma(z_vals)
    
    axes[0].plot(z_vals, gamma_z, label=r'$\Gamma(z)$', color='blue', linewidth=2)
    
    # Values from Section 2.2 of the knowledge base
    table_2_2_z = [1, 2, 3, 4, 0.5, 1.5, 2.5, 3.5]
    table_2_2_gamma = [gamma(z) for z in table_2_2_z]
    
    axes[0].scatter(table_2_2_z, table_2_2_gamma, color='red', zorder=5, 
                    label='Table 2.2 Discrete Values')
    
    # Annotate half-integer points
    for z, g in zip(table_2_2_z[4:], table_2_2_gamma[4:]):
        axes[0].annotate(f"{g:.2f}", (z, g), textcoords="offset points", xytext=(10, -10), fontsize=9)

    axes[0].set_ylim(0, 10)
    axes[0].set_xlim(0, 5.5)
    axes[0].set_title("The Gamma Function $\Gamma(z)$", fontsize=14)
    axes[0].set_xlabel("z")
    axes[0].set_ylabel("$\Gamma(z)$")
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.7)

    # --- GRAPH 2: Fractional Derivatives of f(x) = x^2 ---
    x_cont = np.linspace(0, 5, 200)
    
    y_orig = x_cont**2  # alpha = 0
    # D^(1/2) x^2 = Gamma(3)/Gamma(2.5) * x^(1.5) -> Example 2
    y_half = (gamma(3) / gamma(2.5)) * (x_cont**1.5)
    # D^1 x^2 = 2x
    y_first = 2 * x_cont
    
    axes[1].plot(x_cont, y_orig, label=r'$f(x) = x^2$ ($\alpha=0$)', linestyle='--', color='black')
    axes[1].plot(x_cont, y_half, label=r'$D^{1/2} x^2$ ($\alpha=0.5$)', color='purple', linewidth=2.5)
    axes[1].plot(x_cont, y_first, label=r'$D^1 x^2$ ($\alpha=1$)', linestyle='-.', color='green')
    
    axes[1].set_title("Transition of Orders: Fractional Derivatives of $x^2$", fontsize=14)
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("Derivative Value")
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    output_img = 'fractional_calculus_graphs.png'
    plt.savefig(output_img, dpi=300)
    print(f"Graphs successfully rendered and saved to {output_img}")

if __name__ == "__main__":
    # 1. Generate Mathematical Data
    df_calc = generate_fractional_calculus_data()
    
    # 2. Pivot the Data and Save to Excel
    pivot_table = create_pivot_and_export(df_calc)
    
    # 3. Render Analytical Graphs
    plot_fractional_graphs()
