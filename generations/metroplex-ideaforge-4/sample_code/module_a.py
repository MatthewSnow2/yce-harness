"""Module A - Contains sample classes and functions."""
import os
from pathlib import Path


class BaseClass:
    """A base class for demonstration."""

    def __init__(self, name: str):
        self.name = name

    def greet(self) -> str:
        """Return a greeting."""
        return f"Hello, {self.name}"


class SampleClass(BaseClass):
    """A sample class that extends BaseClass."""

    def __init__(self, name: str, value: int = 0):
        super().__init__(name)
        self.value = value

    def compute(self, x: int) -> int:
        """Compute a value."""
        return self.value + x


def func_a(x: int) -> str:
    """Returns a string representation of x."""
    return str(x)


def helper_func(data: list) -> dict:
    """Transforms a list into a dictionary."""
    return {i: v for i, v in enumerate(data)}
