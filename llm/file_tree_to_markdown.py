#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Optional


def parse_tree_file(tree_file: Path) -> tuple[Path, List[str]]:
    """Parse the tree file and extract base path and all file paths.
    
    Args:
        tree_file: Path to the file containing the tree structure.
        
    Returns:
        Tuple of (base_path, list of relative file paths)
    """
    paths = []
    current_dirs = []
    base_path = None
    prev_level = 0
    
    with open(tree_file) as f:
        for line in f:
            # Parse header for base path
            if line.startswith("#!base_path="):
                base_path = Path(line.strip().split("=", 1)[1])
                continue

            # Skip empty lines
            if not line.strip():
                continue
            
            # Count the actual indent level by looking at the tree characters
            indent = len(line) - len(line.lstrip())
            # Each level consists of 4 characters: either "│   " or "    "
            level = indent // 4
            
            # Clean up the line
            name = (line.strip()
                   .replace('├── ', '')
                   .replace('└── ', '')
                   .replace('│', '')
                   .strip())

            # Handle directory structure
            if level < prev_level:
                # Going back up the tree, remove directories from current path
                current_dirs = current_dirs[:level]
            elif level == prev_level:
                # Same level, replace last directory
                if current_dirs:
                    current_dirs.pop()
            # else: level > prev_level, we'll append the new directory
            
            if '.' in name:  # It's a file
                full_path = '/'.join(current_dirs + [name])
                if full_path not in paths:  # Avoid duplicates
                    paths.append(full_path)
            else:  # It's a directory
                current_dirs.append(name)
            
            prev_level = level
    
    if base_path is None:
        raise ValueError("No base path found in tree file")
        
    return base_path, paths


def generate_markdown(
    tree_file: Path,
    output_file: Path,
    exclude_suffixes: Optional[List[str]] = None,
    exclude_filenames: Optional[List[str]] = None
) -> None:
    """Generate a markdown file containing the contents of all files in the tree.
    
    Args:
        tree_file: Path to the file containing the tree structure
        output_file: Path where to write the markdown output
        exclude_suffixes: List of file suffixes to exclude
        exclude_filenames: List of filenames to exclude
    """
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
        
        # Group files by directory for better organization
        current_dir = None
        for rel_path in sorted(file_paths):
            dir_path = str(Path(rel_path).parent)
            
            # Add directory headers for better organization
            if dir_path != current_dir:
                if dir_path == '.':
                    out_f.write("## Root Directory\n\n")
                else:
                    out_f.write(f"## {dir_path}\n\n")
                current_dir = dir_path
            
            abs_path = base_path / rel_path
            try:
                # Write the file header
                out_f.write(f"### {Path(rel_path).name}\n\n")
                
                # Determine the language for syntax highlighting
                suffix = Path(rel_path).suffix
                lang = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript',
                    '.md': 'markdown',
                    '.json': 'json',
                    '.yaml': 'yaml',
                    '.yml': 'yaml',
                    '.sh': 'bash',
                }.get(suffix, '')
                
                out_f.write(f"```{lang}\n")
                
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
