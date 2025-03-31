"""
Translation utilities for working with translation files and keys.
"""

from typing import Dict, List, Set, Tuple


def check_translation_key_exists(key: str, translation_files: Dict[str, Dict]) -> Dict[str, bool]:
    """
    Check if a translation key exists in all translation files.

    Args:
        key: The translation key to check
        translation_files: Dictionary mapping file keys to translation data

    Returns:
        Dictionary mapping file keys to boolean (exists or not)
    """
    results = {}

    # Parse the key to get namespace and actual key path
    if "." in key:
        namespace, *key_path = key.split(".")
    else:
        # If no namespace specified, can't check
        return results

    # Check each translation file for the namespace
    for file_key, data in translation_files.items():
        file_namespace = file_key.split("/")[0]

        # Skip files from different namespaces
        if file_namespace != namespace:
            continue

        # Navigate through the nested dictionary
        current = data
        key_exists = True

        # Navigate through the rest of the path
        for part in key_path:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                key_exists = False
                break
        results[file_key] = key_exists

    return results


def compare_yaml_files(file1_path: str, file2_path: str, load_yaml_file) -> Tuple[Set[str], Set[str]]:
    """
    Compare two YAML files and identify missing keys.

    Args:
        file1_path: Path to the first YAML file
        file2_path: Path to the second YAML file
        load_yaml_file: Function to load YAML files

    Returns:
        - Keys in file1 but not in file2
        - Keys in file2 but not in file1
    """
    from .yaml_utils import extract_keys

    # Load the YAML files
    data1 = load_yaml_file(file1_path)
    data2 = load_yaml_file(file2_path)

    # Extract all keys from both files
    keys1 = extract_keys(data1)
    keys2 = extract_keys(data2)

    # Find missing keys
    missing_in_file2 = keys1 - keys2
    missing_in_file1 = keys2 - keys1

    return missing_in_file2, missing_in_file1
