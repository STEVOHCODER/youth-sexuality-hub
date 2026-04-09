import sympy as sp
import datetime

class PyodideScientificCalculator:
    """
    A robust scientific calculator engineered for WebAssembly/Pyodide environments.
    Utilizes symbolic computation to process advanced mathematical operations.
    """
    def __init__(self):
        # Acts as an in-memory ledger (replacing the SQLite database)
        self.ledger = []

    def evaluate(self, expression: str):
        """
        Parses and evaluates mathematical strings mathematically.
        Supports trigonometry (sin, cos), logarithms, and constants (pi, E).
        """
        try:
            # Sanitize standard calculator UI inputs to Python operators
            expr_str = expression.replace('×', '*').replace('÷', '/')
            
            # Mathematical evaluation using SymPy's symbolic parsing
            expr = sp.sympify(expr_str)
            
            # Evaluate to a floating point number
            result = float(expr.evalf())
            
            # Record state in the ledger
            self.ledger.append({
                "expression": expression,
                "result": result,
                "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return result
        
        except Exception as e:
            return f"Mathematical Syntax Error: Ensure valid notation. Details: {e}"

    def view_ledger(self):
        """Outputs the historical calculations."""
        print(f"\n{'='*40}")
        print(f"{'CALCULATION LEDGER':^40}")
        print(f"{'='*40}")
        if not self.ledger:
            print("No records found.")
        else:
            for entry in self.ledger:
                # Format to 4 decimal places for clean scientific display
                formatted_result = f"{entry['result']:.4f}".rstrip('0').rstrip('.')
                print(f"[{entry['timestamp']}]  {entry['expression']} = {formatted_result}")
        print(f"{'='*40}\n")

# ==========================================
# Instantiation and Execution Sandbox
# ==========================================

# 1. Initialize the Architect's Engine
calc = PyodideScientificCalculator()

# 2. Perform Advanced Evaluations (Testing trigonometric and exponential bounds)
print("Calculation 1 (Trigonometry):", calc.evaluate("sin(pi / 2) + cos(0)"))
print("Calculation 2 (Exponentials):", calc.evaluate("2**10 - 24"))
print("Calculation 3 (Logarithms)  :", calc.evaluate("log(1000, 10)"))
print("Calculation 4 (Fractions)   :", calc.evaluate("(50 + 25) ÷ 3"))

# 3. View the persistent memory ledger
calc.view_ledger()
