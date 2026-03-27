"""Data models for representing code symbols."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Symbol:
    """Base symbol class."""
    name: str
    docstring: Optional[str] = None


@dataclass
class FunctionSymbol(Symbol):
    """Represents a function or method."""
    signature: str = ""  # e.g., "foo(x: int, y: str = \"\") -> bool"


@dataclass
class ClassSymbol(Symbol):
    """Represents a class definition."""
    bases: List[str] = field(default_factory=list)
    methods: List[FunctionSymbol] = field(default_factory=list)


@dataclass
class ModuleSymbol(Symbol):
    """Represents a Python module."""
    path: str = ""
    classes: List[ClassSymbol] = field(default_factory=list)
    functions: List[FunctionSymbol] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
