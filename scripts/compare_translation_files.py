#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translation file comparison tool.

This script:
1. Loads two translation files (YAML format)
2. Compares the keys in both files
3. Reports keys that are present in one file but missing in the other
"""

import os
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


def load_yaml_file(file_path: str) -> Dict:
    """Load a YAML file and return its contents as a dictionary."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}


def extract_keys(data: Dict, prefix: str = "") -> Set[str]:
    """
    Recursively extract all keys from a nested dictionary.

    Returns a set of dot-separated key paths.
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


def compare_yaml_files(file1_path: str, file2_path: str) -> Tuple[Set[str], Set[str]]:
    """
    Compare two YAML files and identify missing keys.

    Returns:
        - Keys in file1 but not in file2
        - Keys in file2 but not in file1
    """
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


def find_translation_files(base_dir: str) -> Dict[str, List[str]]:
    """
    Find all translation files in the project.

    Returns a dictionary mapping namespaces to lists of file paths.
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


def main():
    parser = argparse.ArgumentParser(description="Compare translation files for missing keys")
    parser.add_argument("--file1", help="First translation file")
    parser.add_argument("--file2", help="Second translation file")
    parser.add_argument("--dir", default=".", help="Base directory to scan for translation files")
    parser.add_argument("--list", action="store_true", help="List available translation files")
    parser.add_argument("--namespace", help="Compare all files in a specific namespace")
    args = parser.parse_args()

    print("Note: Only comparing translation files in the 'cosmotech' directory")

    # If list flag is provided, just list available translation files
    if args.list:
        translation_files = find_translation_files(args.dir)

        print("Available translation files:")
        for namespace, files in translation_files.items():
            print(f"\nNamespace: {namespace}")
            for file_path in files:
                print(f"  {file_path}")

        return

    # If namespace is provided, compare all files in that namespace
    if args.namespace:
        translation_files = find_translation_files(args.dir)

        if args.namespace not in translation_files:
            print(f"Namespace '{args.namespace}' not found")
            return

        files = list(sorted(translation_files[args.namespace]))

        if len(files) < 2:
            print(f"Not enough files in namespace '{args.namespace}' to compare")
            return

        # Compare each pair of files
        for j in range(1, len(files)):
            file1_path = files[0]
            file2_path = files[j]

            print("\nComparing:")
            print(f"  File 1: {file1_path}")
            print(f"  File 2: {file2_path}")

            missing_in_file2, missing_in_file1 = compare_yaml_files(file1_path, file2_path)

            print("\nKeys in File 1 but missing in File 2:")
            if missing_in_file2:
                for key in sorted(missing_in_file2):
                    print(f"  {key}")
            else:
                print("  None")

            print("\nKeys in File 2 but missing in File 1:")
            if missing_in_file1:
                for key in sorted(missing_in_file1):
                    print(f"  {key}")
            else:
                print("  None")

        return

    # If specific files are provided, compare them
    if args.file1 and args.file2:
        file1_path = args.file1
        file2_path = args.file2

        if not os.path.exists(file1_path):
            print(f"File not found: {file1_path}")
            return

        if not os.path.exists(file2_path):
            print(f"File not found: {file2_path}")
            return

        print(f"\nComparing:")
        print(f"  File 1: {file1_path}")
        print(f"  File 2: {file2_path}")

        missing_in_file2, missing_in_file1 = compare_yaml_files(file1_path, file2_path)

        print("\nKeys in File 1 but missing in File 2:")
        if missing_in_file2:
            for key in sorted(missing_in_file2):
                print(f"  {key}")
        else:
            print("  None")

        print("\nKeys in File 2 but missing in File 1:")
        if missing_in_file1:
            for key in sorted(missing_in_file1):
                print(f"  {key}")
        else:
            print("  None")

        return

    # If we get here, not enough arguments were provided
    parser.print_help()


if __name__ == "__main__":
    main()
