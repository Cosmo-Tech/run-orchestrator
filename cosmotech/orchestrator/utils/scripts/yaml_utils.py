"""
YAML file utilities for loading and processing YAML files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Set


def load_yaml_file(file_path: str) -> Dict:
    """
    Load a YAML file and return its contents as a dictionary.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dictionary containing the YAML file contents or empty dict if error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}


def load_translation_files(base_dir: str) -> Dict[str, Dict]:
    """
    Load all translation YAML files.

    Args:
        base_dir: Base directory to search for translation files

    Returns:
        Dictionary mapping file keys to translation data
    """
    translation_files = {}

    # Find all translation directories
    translation_dir = Path(base_dir) / "translation"
    if not translation_dir.exists():
        return translation_files

    # Recursively find all .yml files
    for yml_file in translation_dir.glob("**/*.yml"):
        # Get relative path components
        rel_path = yml_file.relative_to(translation_dir)
        components = list(rel_path.parts)

        if len(components) >= 2 and "rich" not in components:
            # Format: {namespace}/{locale}/{filename}.yml
            namespace = components[0]
            locale = components[1]

            try:
                with open(yml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                key = f"{namespace}/{locale}"
                translation_files[key] = data
            except Exception as e:
                print(f"Error loading {yml_file}: {e}")

    return translation_files


def extract_keys(data: Dict, prefix: str = "") -> Set[str]:
    """
    Recursively extract all keys from a nested dictionary.

    Args:
        data: Dictionary to extract keys from
        prefix: Prefix for nested keys

    Returns:
        Set of dot-separated key paths
    """
    keys = set()

    if not isinstance(data, dict):
        return keys

    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.add(full_key)

        if isinstance(value, dict):
            # Recursively extract keys from nested dictionaries
            nested_keys = extract_keys(value, full_key)
            keys.update(nested_keys)

    return keys


def print_yaml_structure(data, prefix=""):
    """
    Debug function to print the structure of a YAML file.

    Args:
        data: YAML data to print
        prefix: Indentation prefix for nested structures
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                print_yaml_structure(value, prefix + "  ")
            else:
                print(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{prefix}[{i}]:")
            print_yaml_structure(item, prefix + "  ")
    else:
        print(f"{prefix}{data}")
