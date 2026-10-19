"""Extends the Calculator class from Mini Project 1 for the web API."""
import sys
from pathlib import Path

# Mini Project 1 is a Git submodule; make its custom_classes.py importable
sys.path.append(str(Path(__file__).resolve().parent.parent / "EE471_MP1_Calculator"))

from custom_classes import Calculator  # noqa: E402


def is_number(value):
    # JSON true/false become bool, which Python also treats as int
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class WebCalculator(Calculator):
    """Mini Project 1 Calculator with input checks and one entry point."""

    def divide(self, x, y):
        if y == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return super().divide(x, y)

    def calculate(self, a, operator, b):
        if not is_number(a) or not is_number(b):
            raise ValueError("a and b must be numbers")

        # No eval(): each operator is mapped to a Calculator method
        if operator == "+":
            result = self.add(a, b)
        elif operator == "-":
            result = self.subtract(a, b)
        elif operator == "*":
            result = self.multiply(a, b)
        elif operator == "/":
            result = self.divide(a, b)
        else:
            raise ValueError("operator must be one of + - * /")

        # Removes floating-point noise (0.1 + 0.2 = 0.30000000000000004)
        # and keeps results short enough for the display
        return round(result, 8)
