```bash
#!/bin/bash

# Function to add two numbers
add() {
    echo $(($1 + $2))
}

# Function to subtract two numbers
subtract() {
    echo $(($1 - $2))
}

# Function to multiply two numbers
multiply() {
    echo $(($1 * $2))
}

# Function to divide two numbers
divide() {
    if [ "$2" -eq 0 ]; then
        echo "Error: Division by zero"
    else
        echo $(echo "scale=2; $1 / $2" | bc)
    fi
}

# Main function to display options and take user input
main() {
    echo "Select an option:"
    echo "1. Add"
    echo "2. Subtract"
    echo "3. Multiply"
    echo "4. Divide"
    read choice

    echo "Enter the first number:"
    read num1

    echo "Enter the second number:"
    read num2

    case $choice in
        1)
            result=$(add "$num1" "$num2")
            echo "Result: $result"
            ;;
        2)
            result=$(subtract "$num1" "$num2")
            echo "Result: $result"
            ;;
        3)
            result=$(multiply "$num1" "$num2")
            echo "Result: $result"
            ;;
        4)
            result=$(divide "$num1" "$num2")
            echo "Result: $result"
            ;;
        *)
            echo "Invalid option. Please try again."
            main
            ;;
    esac
}

# Run the main function
main
```