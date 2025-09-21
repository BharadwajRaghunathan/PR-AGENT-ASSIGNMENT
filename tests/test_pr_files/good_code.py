class Calculator:
    """A simple calculator class."""
    def add(self, a, b):
        """Adds two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtracts b from a."""
        return a - b

    def multiply(self, a, b):
        """Multiplies two numbers."""
        return a * b

    def divide(self, a, b):
        """Divides a by b, with error handling."""
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b