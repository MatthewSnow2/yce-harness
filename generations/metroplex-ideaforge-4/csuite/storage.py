"""JSON cache storage (placeholder for future optimization)."""
import json
from pathlib import Path
from typing import List
from .models import ModuleSymbol


def save_to_cache(modules: List[ModuleSymbol], cache_path: Path) -> None:
    """
    Save parsed modules to a JSON cache file.

    This is a placeholder for future optimization.
    """
    raise NotImplementedError("JSON caching will be implemented in a future feature")


def load_from_cache(cache_path: Path) -> List[ModuleSymbol]:
    """
    Load parsed modules from a JSON cache file.

    This is a placeholder for future optimization.
    """
    raise NotImplementedError("JSON caching will be implemented in a future feature")
