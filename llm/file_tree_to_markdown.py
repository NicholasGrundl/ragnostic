#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Optional, Set


def parse_tree_file(tree_file: Path) -> tuple[Path, List[str]]:
    """Parse the tree file and extract base path and all file paths.
    
    Args:
        tree_file: Path to the file containing the tree structure.
        
    Returns:
        Tuple of (base_path, list of relative file paths)
    """
    paths = []
    current_path_parts = []
    base_path = None
    
    with open(tree_file) as f:
        for line in f:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Parse header for base path
            if line.startswith("#!base_path="):
                base_path = Path(line.strip().split("=", 1)[1])
                continue
                
            # Count the level of indentation
            indent_level = (len(line) - len(line.lstrip())) // 4
            
            # Clean up the line - remove tree characters and whitespace
            clean_line = line.strip().replace('├── ', '').replace('└── ', '').replace('│   ', '')
            
            # Adjust the current path based on indentation
            current_path_parts = current_path_parts[:indent_level]
            current_path_parts.append(clean_line)
            
            # Only add paths that look like files (have an extension or are __init__.py)
            if '.' in clean_line or clean_line == '__init__.py':
                paths.append('/'.join(current_path_parts))
    
    if base_path is None:
        raise ValueError("No base path found in tree file")
        
    return base_path, paths

def generate_markdown(
    tree_file: Path,
    output_file: Path,
    exclude_suffixes: Optional[List[str]] = None,
    exclude_filenames: Optional[List[str]] = None
) -> None:
    """Generate a markdown file containing the contents of all files in the tree."""
    exclude_suffixes = set(exclude_suffixes or [])
    exclude_filenames = set(exclude_filenames or [])
    
    def should_include(path: str) -> bool:
        name = Path(path).name
        suffix = Path(path).suffix
        return (
            suffix not in exclude_suffixes and
            name not in exclude_filenames and
            not any(part.startswith('.') for part in Path(path).parts)
        )
    
    # Get base path and file paths from the tree
    base_path, relative_paths = parse_tree_file(tree_file)
    file_paths = [
        path for path in relative_paths
        if should_include(path)
    ]
    
    # Generate the markdown content
    with open(output_file, 'w') as out_f:
        out_f.write("# Project Source Code\n\n")
        out_f.write(f"Base path: `{base_path}`\n\n")
        
        for rel_path in file_paths:
            abs_path = base_path / rel_path
            try:
                # Write the file header
                out_f.write(f"## {rel_path}\n\n")
                out_f.write("```python\n")
                
                # Write the file contents
                with open(abs_path) as in_f:
                    out_f.write(in_f.read())
                
                out_f.write("```\n\n")
            except FileNotFoundError:
                out_f.write(f"*File not found: {abs_path}*\n\n")
            except Exception as e:
                out_f.write(f"*Error reading file: {abs_path} - {str(e)}*\n\n")

def main():
    """Parse command line arguments and run the markdown generator."""
    parser = argparse.ArgumentParser(
        description="Generate a markdown file containing all source code from a file tree.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "tree_file",
        type=str,
        help="Input file containing the tree structure"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="SOURCE_CODE.md",
        help="Output markdown file path"
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
        default=["__pycache__"],
        help="List of filenames to exclude"
    )
    
    args = parser.parse_args()
    
    try:
        generate_markdown(
            tree_file=Path(args.tree_file),
            output_file=Path(args.output),
            exclude_suffixes=args.exclude_suffixes,
            exclude_filenames=args.exclude_filenames
        )
    except Exception as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()