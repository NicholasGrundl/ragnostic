#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Optional


def generate_file_tree(
    directory: str | Path,
    level: int = 10,  # Increased default depth
    exclude_suffixes: Optional[List[str]] = None,
    exclude_filenames: Optional[List[str]] = None,
    include_base_path: bool = False
) -> str:
    """Generate a file tree string representation starting from the given directory.
    
    Args:
        directory: Path to the root directory.
        level: Maximum depth level to traverse (default: 10).
        exclude_suffixes: List of file suffixes to exclude (default: None).
        exclude_filenames: List of filenames to exclude (default: None).
        include_base_path: Whether to include the base path in the output (default: False).
    
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
        if current_level < 1 or not should_include(path):
            return ""
        
        result = [path.name if not prefix else f"{prefix}{path.name}"]
        
        if path.is_dir() and current_level > 1:
            items = sorted(
                [p for p in path.iterdir() if should_include(p)],
                key=lambda x: (not x.is_dir(), x.name)
            )
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                if not prefix:
                    new_prefix = "├── " if not is_last else "└── "
                else:
                    new_prefix = prefix.replace("└── ", "    ").replace("├── ", "│   ")
                    new_prefix += "├── " if not is_last else "└── "
                
                subtree = build_tree(item, current_level - 1, new_prefix)
                if subtree:
                    result.append(subtree)
        
        return "\n".join(result)
    
    tree = build_tree(root, level)
    if include_base_path:
        # Add header with absolute path
        header = f"#!base_path={root.resolve()}\n"
        return header + tree
    return tree


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
        default=10,  # Increased default depth
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
    
    parser.add_argument(
        "-b", "--include-base-path",
        action="store_true",
        help="Include the base path in the output"
    )

    args = parser.parse_args()
    
    try:
        tree = generate_file_tree(
            directory=args.directory,
            level=args.level,
            exclude_suffixes=args.exclude_suffixes,
            exclude_filenames=args.exclude_filenames,
            include_base_path=args.include_base_path,
        )
        print(tree)
    except ValueError as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()