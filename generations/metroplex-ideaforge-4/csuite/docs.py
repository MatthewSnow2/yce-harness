"""Markdown documentation generation for Feature 3."""
from typing import List
from .models import ModuleSymbol, ClassSymbol, FunctionSymbol


def generate_markdown_docs(modules: List[ModuleSymbol], base_package: str = None) -> str:
    """
    Generate Markdown documentation from parsed modules.

    Args:
        modules: List of ModuleSymbol objects representing the parsed codebase
        base_package: Optional base package name to prepend to module names

    Returns:
        str: Complete Markdown documentation with table of contents
    """
    lines = []

    # Infer base package from common path if not provided
    if base_package is None and modules:
        base_package = _infer_base_package(modules)

    # Generate table of contents
    lines.append("# Table of Contents")
    lines.append("")

    for module in modules:
        module_name = _get_module_display_name(module.name, module.path, base_package)
        anchor = _generate_anchor(module_name)
        lines.append(f"- [Module: {module_name}](#{anchor})")

    lines.append("")

    # Generate documentation for each module
    for module in modules:
        module_name = _get_module_display_name(module.name, module.path, base_package)
        lines.append(f"## Module: {module_name}")
        lines.append("")

        # Add module docstring if available
        if module.docstring:
            lines.append(module.docstring)
            lines.append("")

        # Document classes
        if module.classes:
            lines.append("### Classes")
            lines.append("")

            for cls in module.classes:
                lines.extend(_format_class(cls))

            lines.append("")

        # Document functions
        if module.functions:
            lines.append("### Functions")
            lines.append("")

            for func in module.functions:
                lines.extend(_format_function(func))

            lines.append("")

    return "\n".join(lines)


def _infer_base_package(modules: List[ModuleSymbol]) -> str:
    """
    Infer the base package name from module paths.

    If there are subdirectories in paths, use the first directory name.
    Otherwise, return empty string.

    Args:
        modules: List of ModuleSymbol objects

    Returns:
        str: Base package name or empty string
    """
    # Look for modules with directory paths
    for module in modules:
        path = module.path
        if '/' in path or '\\' in path:
            # Extract first directory
            parts = path.replace('\\', '/').split('/')
            if len(parts) > 1:
                return parts[0]
    return ""


def _get_module_display_name(module_name: str, module_path: str, base_package: str = None) -> str:
    """
    Convert a module path to a display name in dotted notation.

    Args:
        module_name: The module name (e.g., 'module_a.py')
        module_path: The module path (e.g., 'module_a.py')
        base_package: Optional base package to prepend

    Returns:
        str: Display name like 'sample_code.module_a'
    """
    # Remove .py extension
    path = module_path.replace('.py', '')
    # Replace path separators with dots
    path = path.replace('/', '.').replace('\\', '.')

    # If we have a base package and the path doesn't start with it, prepend it
    if base_package and not path.startswith(base_package):
        if path == '__init__':
            return base_package
        else:
            return f"{base_package}.{path}"

    return path


def _generate_anchor(module_name: str) -> str:
    """
    Generate a Markdown anchor from a module name following GitHub/CommonMark rules.

    Args:
        module_name: Module name like 'sample_code.module_a'

    Returns:
        str: Anchor like 'module-sample_codemodule_a'
    """
    # Build the full heading text
    heading_text = f"Module: {module_name}"

    # GitHub/CommonMark anchor rules:
    # 1. Convert to lowercase
    # 2. Replace spaces with hyphens
    # 3. Remove special characters except hyphens and underscores
    anchor = heading_text.lower()
    anchor = anchor.replace(' ', '-')

    # Remove special characters (keep only alphanumeric, hyphens, and underscores)
    sanitized = []
    for char in anchor:
        if char.isalnum() or char in ('-', '_'):
            sanitized.append(char)

    return ''.join(sanitized)


def _format_class(cls: ClassSymbol) -> List[str]:
    """
    Format a class for Markdown documentation.

    Args:
        cls: ClassSymbol to format

    Returns:
        List[str]: Lines of Markdown text
    """
    lines = []

    # Class header with name and bases
    header = f"- **{cls.name}**"
    if cls.bases:
        bases_str = ", ".join(cls.bases)
        header += f" (extends: {bases_str})"

    # Add docstring if available
    if cls.docstring:
        docstring_first_line = cls.docstring.split('\n')[0].strip()
        header += f" — {docstring_first_line}"

    lines.append(header)

    # Add methods if any
    if cls.methods:
        lines.append("  - Methods:")
        for method in cls.methods:
            method_line = f"    - `{method.signature}`"
            if method.docstring:
                docstring_first_line = method.docstring.split('\n')[0].strip()
                method_line += f" — {docstring_first_line}"
            lines.append(method_line)

    return lines


def _format_function(func: FunctionSymbol) -> List[str]:
    """
    Format a function for Markdown documentation.

    Args:
        func: FunctionSymbol to format

    Returns:
        List[str]: Lines of Markdown text
    """
    lines = []

    # Function header with signature
    header = f"- **{func.signature}**"

    # Add docstring if available
    if func.docstring:
        docstring_first_line = func.docstring.split('\n')[0].strip()
        header += f" — {docstring_first_line}"

    lines.append(header)

    return lines
