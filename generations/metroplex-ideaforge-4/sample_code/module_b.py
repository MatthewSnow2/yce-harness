"""Module B - Contains more sample classes."""
from .module_a import SampleClass


class AnotherClass:
    """Another class for testing."""

    def __init__(self):
        self.items = []

    def add_item(self, item: str) -> None:
        """Add an item to the list."""
        self.items.append(item)

    def get_items(self) -> list:
        """Return all items."""
        return self.items


class ChildClass(SampleClass):
    """A child class that extends SampleClass."""

    def compute(self, x: int) -> int:
        """Override compute with multiplication."""
        return self.value * x


def func_b(text: str) -> str:
    """Process text by stripping and lowering."""
    return text.strip().lower()
