"""
File system utilities for finding and processing files.
"""

import os
from pathlib import Path
from typing import Dict, List, Set


def find_python_files(directory: str) -> List[str]:
    """
    Find all Python files in a directory recursively.

    Args:
        directory: The directory to search in

    Returns:
        A list of paths to Python files
    """
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def find_translation_files(base_dir: str) -> Dict[str, List[str]]:
    """
    Find all translation files in the project.

    Args:
        base_dir: The base directory to search in

    Returns:
        A dictionary mapping namespaces to lists of file paths
    """
    translation_files = {}

    # Find all translation directories
    translation_dir = Path(base_dir) / "cosmotech" / "translation"
    if not translation_dir.exists():
        return translation_files

    # Recursively find all .yml files
    for yml_file in translation_dir.glob("**/*.yml"):
        # Get relative path components
        rel_path = yml_file.relative_to(translation_dir)
        components = list(rel_path.parts)

        if len(components) >= 2:
            # Format: {namespace}/{locale}/{filename}.yml
            namespace = components[0]

            if namespace not in translation_files:
                translation_files[namespace] = []

            translation_files[namespace].append(str(yml_file))

    return translation_files
