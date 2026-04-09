import React, { useState } from 'react';

const Calculator = () => {
  const [currentNumber, setCurrentNumber] = useState('');
  const [operator, setOperator] = useState(null);
  const [storedValue, setStoredValue] = useState(null);

  const handleButtonClick = (value) => {
    if (['+', '-', '*', '/'].includes(value)) {
      if (waitingForSecondOperand) {
        operator = value;
        setStoredValue(parseFloat(currentNumber));
        setCurrentNumber('');
      } else {
        setOperator(value);
      }
      waitingForSecondOperand = true;
    } else {
      currentNumber += value.toString();
      setCurrentNumber(currentNumber);
    }
  };

  const handleEqualClick = () => {
    if (waitingForSecondOperand) {
      const currentValue = parseFloat(currentNumber);
      let result = 0;

      switch (operator) {
        case '+':
          result = currentValue + storedValue;
          break;
        case '-':
          result = currentValue - storedValue;
          break;
        case '*':
          result = currentValue * storedValue;
          break;
        case '/':
          if (storedValue !== 0) {
            result = currentValue / storedValue;
          } else {
            alert("Cannot divide by zero");
          }
          break;
      }

      setCurrentNumber(result.toString());
      setStoredValue(null);
      operator = null;
    }
  };

  const handleClearClick = () => {
    setCurrentNumber('');
    setOperator(null);
    setStoredValue(null);
  };

  return (
    <div className="calculator">
      <input
        type="text"
        readOnly
        value={currentNumber}
        className="calculator-screen"
      />
      <div className="calculator-buttons">
        {['7', '8', '9', '/'].map((value) => (
          <button key={value} onClick={() => handleButtonClick(value)}>
            {value}
          </button>
        ))}
        <button onClick={() => handleOperator('*')}>*</button>
        <button onClick={() => handleOperator('-')}>-</button>
        <button onClick={() => handleOperator('+')}>+</button>
        <button onClick={handleEqualClick}>=</button>
        <button onClick={handleClearClick}>C</button>
      </div>
    </div>
  );
};

export default Calculator;
