"""Utility functions for csuite."""
import ast
from pathlib import Path
from typing import List


def should_skip_directory(path: Path) -> bool:
    """Check if a directory should be skipped during traversal."""
    skip_dirs = {'.git', '__pycache__', '.venv', 'venv', '.tox', '.eggs',
                 'node_modules', '.pytest_cache', '.mypy_cache', 'dist', 'build'}
    return path.name in skip_dirs


def collect_python_files(root_path: Path) -> List[Path]:
    """
    Recursively collect all .py files from root_path,
    skipping common VCS and build directories.
    """
    python_files = []

    def walk_directory(path: Path):
        if not path.exists():
            return

        if path.is_file() and path.suffix == '.py':
            python_files.append(path)
        elif path.is_dir():
            if should_skip_directory(path):
                return
            try:
                for item in path.iterdir():
                    walk_directory(item)
            except PermissionError:
                pass  # Skip directories we can't read

    walk_directory(root_path)
    return sorted(python_files)


def format_function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """
    Format a function signature from an AST node.

    Example output: "foo(x: int, y: str = '') -> bool"
    """
    args_parts = []

    # Handle positional arguments
    defaults_offset = len(node.args.args) - len(node.args.defaults)

    for i, arg in enumerate(node.args.args):
        arg_str = arg.arg

        # Add type annotation if present
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"

        # Add default value if present
        default_index = i - defaults_offset
        if default_index >= 0:
            default = node.args.defaults[default_index]
            arg_str += f" = {ast.unparse(default)}"

        args_parts.append(arg_str)

    # Handle *args
    if node.args.vararg:
        vararg_str = f"*{node.args.vararg.arg}"
        if node.args.vararg.annotation:
            vararg_str += f": {ast.unparse(node.args.vararg.annotation)}"
        args_parts.append(vararg_str)

    # Handle keyword-only arguments
    kw_defaults_dict = {kw.arg: default for kw, default in
                        zip(node.args.kwonlyargs, node.args.kw_defaults)
                        if default is not None}

    for kwarg in node.args.kwonlyargs:
        kwarg_str = kwarg.arg
        if kwarg.annotation:
            kwarg_str += f": {ast.unparse(kwarg.annotation)}"
        if kwarg.arg in kw_defaults_dict:
            kwarg_str += f" = {ast.unparse(kw_defaults_dict[kwarg.arg])}"
        args_parts.append(kwarg_str)

    # Handle **kwargs
    if node.args.kwarg:
        kwarg_str = f"**{node.args.kwarg.arg}"
        if node.args.kwarg.annotation:
            kwarg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
        args_parts.append(kwarg_str)

    signature = f"{node.name}({', '.join(args_parts)})"

    # Add return type annotation if present
    if node.returns:
        signature += f" -> {ast.unparse(node.returns)}"

    return signature


def get_docstring(node: ast.AST) -> str | None:
    """Extract docstring from an AST node."""
    return ast.get_docstring(node)
