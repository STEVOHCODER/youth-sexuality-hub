```python
# Import necessary library
import sys

def calculate(expression):
    # Split the expression into tokens
    tokens = expression.split()
    
    # Check if the expression is valid
    if len(tokens) < 3:
        print("Invalid expression")
        return None
    
    # Initialize variables
    num1 = float(tokens[0])
    operator = tokens[1]
    num2 = float(tokens[2])
    
    # Perform the operation based on the operator
    if operator == '+':
        result = num1 + num2
    elif operator == '-':
        result = num1 - num2
    elif operator == '*':
        result = num1 * num2
    elif operator == '/':
        if num2 != 0:
            result = num1 / num2
        else:
            print("Error: Division by zero")
            return None
    
    # Return the result
    return result

def main():
    # Check if an argument is provided
    if len(sys.argv) != 3:
        print("Usage: python math_calculator.py <expression>")
        return
    
    # Calculate and display the result
    expression = sys.argv[1]
    result = calculate(expression)
    if result is not None:
        print(f"The result of {expression} is {result}")

if __name__ == "__main__":
    main()
```