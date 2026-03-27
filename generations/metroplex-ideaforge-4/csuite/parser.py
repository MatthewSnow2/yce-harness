"""AST-based parser for extracting code symbols."""
import ast
from pathlib import Path
from typing import List

from .models import ModuleSymbol, ClassSymbol, FunctionSymbol
from .utils import collect_python_files, format_function_signature, get_docstring


class CodebaseParser:
    """Parses a Python codebase and extracts symbols."""

    def __init__(self, root_path: str | Path):
        self.root_path = Path(root_path).resolve()
        self.modules: List[ModuleSymbol] = []

    def parse(self) -> List[ModuleSymbol]:
        """Parse all Python files in the codebase."""
        python_files = collect_python_files(self.root_path)

        for file_path in python_files:
            module = self._parse_file(file_path)
            if module:
                self.modules.append(module)

        return self.modules

    def _parse_file(self, file_path: Path) -> ModuleSymbol | None:
        """Parse a single Python file and extract symbols."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError, OSError) as e:
            # Skip files that can't be parsed
            return None

        # Create relative path for module name
        try:
            relative_path = file_path.relative_to(self.root_path)
        except ValueError:
            relative_path = file_path

        module_name = str(relative_path)
        module = ModuleSymbol(
            name=module_name,
            path=str(relative_path),
            docstring=get_docstring(tree)
        )

        # Walk the AST and extract symbols
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module.imports.append(node.module)

        # Extract top-level classes and functions
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_symbol = self._parse_class(node)
                module.classes.append(class_symbol)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_symbol = self._parse_function(node)
                module.functions.append(func_symbol)

        return module

    def _parse_class(self, node: ast.ClassDef) -> ClassSymbol:
        """Parse a class definition."""
        # Extract base classes
        bases = []
        for base in node.bases:
            try:
                base_name = ast.unparse(base)
                bases.append(base_name)
            except Exception:
                bases.append(str(base))

        class_symbol = ClassSymbol(
            name=node.name,
            docstring=get_docstring(node),
            bases=bases
        )

        # Extract methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._parse_function(item)
                class_symbol.methods.append(method)

        return class_symbol

    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionSymbol:
        """Parse a function or method definition."""
        signature = format_function_signature(node)

        return FunctionSymbol(
            name=node.name,
            docstring=get_docstring(node),
            signature=signature
        )

    def get_summary(self) -> dict:
        """Get a summary of parsed symbols."""
        total_classes = sum(len(m.classes) for m in self.modules)
        total_functions = sum(len(m.functions) for m in self.modules)
        total_methods = sum(
            len(cls.methods)
            for m in self.modules
            for cls in m.classes
        )
        total_imports = sum(len(m.imports) for m in self.modules)

        return {
            'modules': len(self.modules),
            'classes': total_classes,
            'functions': total_functions + total_methods,
            'imports': total_imports
        }
