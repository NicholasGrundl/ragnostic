#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Optional


def generate_file_tree(
    directory: str | Path,
    level: int = 3,
    exclude_suffixes: Optional[List[str]] = None,
    exclude_filenames: Optional[List[str]] = None,
) -> str:
    """Generate a file tree string representation starting from the given directory.
    
    Args:
        directory: Path to the root directory.
        level: Maximum depth level to traverse (default: 3).
        exclude_suffixes: List of file suffixes to exclude (default: None).
        exclude_filenames: List of filenames to exclude (default: None).
    
    Returns:
        str: String representation of the file tree.
    
    Raises:
        ValueError: If directory doesn't exist or level is less than 1.
    """
    root = Path(directory)
    if not root.exists():
        raise ValueError(f"Directory {directory} does not exist")
    if level < 1:
        raise ValueError("Level must be at least 1")
    
    exclude_suffixes = set(exclude_suffixes or [])
    exclude_filenames = set(exclude_filenames or [])
    
    def should_include(path: Path) -> bool:
        return (
            path.suffix not in exclude_suffixes and
            path.name not in exclude_filenames
        )
    
    def build_tree(path: Path, current_level: int, prefix: str = "") -> str:
        if current_level < 1:
            return ""
        
        if not path.is_dir():
            return f"{prefix}└── {path.name}\n" if should_include(path) else ""
        
        result = []
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        
        for i, item in enumerate(items):
            if not should_include(item):
                continue
                
            is_last = i == len(items) - 1
            current_prefix = prefix + ("└── " if is_last else "├── ")
            next_prefix = prefix + ("    " if is_last else "│   ")
            
            result.append(current_prefix + item.name)
            subtree = build_tree(item, current_level - 1, next_prefix)
            if subtree:
                result.append(subtree.rstrip())
        
        return "\n".join(result) + "\n"
    
    return build_tree(root, level)


def main():
    """Parse command line arguments and run the file tree generator."""
    parser = argparse.ArgumentParser(
        description="Generate a file tree representation of a directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "-d", "--directory",
        type=str,
        default=".",
        help="Root directory to start from"
    )
    
    parser.add_argument(
        "-l", "--level",
        type=int,
        default=3,
        help="Maximum depth level to traverse"
    )
    
    parser.add_argument(
        "-s", "--exclude-suffixes",
        nargs="*",
        default=[".pyc", ".pyo", ".pyd"],
        help="List of file suffixes to exclude"
    )
    
    parser.add_argument(
        "-f", "--exclude-filenames",
        nargs="*",
        default=["__pycache__", ".git", ".pytest_cache"],
        help="List of filenames to exclude"
    )
    
    args = parser.parse_args()
    
    try:
        tree = generate_file_tree(
            directory=args.directory,
            level=args.level,
            exclude_suffixes=args.exclude_suffixes,
            exclude_filenames=args.exclude_filenames
        )
        print(tree)
    except ValueError as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()