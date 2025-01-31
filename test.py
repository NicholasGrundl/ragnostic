#!/usr/bin/env python3
"""Parse markdown tree structure and return full file paths."""

import re
from pathlib import Path
from typing import List


def parse_tree_structure(markdown_text: str) -> tuple[str, List[str]]:
    """
    Parse markdown tree structure and return base path and all file paths.
    
    Args:
        markdown_text: String containing markdown tree structure
    
    Returns:
        Tuple containing base path and list of file paths (excluding directories)
    """
    # Extract base path from first line if present
    lines = markdown_text.strip().split('\n')
    base_path = ''
    start_idx = 0
    
    if lines[0].startswith('#!base_path='):
        base_path = lines[0].split('=')[1].strip()
        start_idx = 1
    
    paths = []
    current_path_components = []
    last_depth = -1
    
    for line in lines[start_idx:]:
        if not line.strip() or '│' in line:
            continue
            
        # Count the depth based on the number of spaces
        indent_match = re.match(r'^(\s*)[└├]──\s+(.+)$', line)
        if not indent_match:
            # Handle root directory case
            if not line.startswith(' '):
                current_path_components = [line.strip()]
            continue
            
        indent, name = indent_match.groups()
        depth = len(indent) // 4  # Assuming 4 spaces per level
        
        # Adjust the path components based on depth
        if depth <= last_depth:
            current_path_components = current_path_components[:depth]
        
        current_path_components.append(name)
        last_depth = depth
        
        # Only add paths that have a file extension (i.e., not directories)
        if '.' in name:
            paths.append(Path(*current_path_components))
    
    # Convert paths to strings and add base_path
    full_paths = [
        str(Path(base_path) / path) for path in paths
    ]
    
    return base_path, sorted(full_paths)

def main():
    """Main function to demonstrate usage."""
    # Example usage
    with open('test.md', 'r') as f:
        markdown_text = f.read()
    
    base_path, paths = parse_tree_structure(markdown_text)
    
    print(f"Base path: {base_path}")
    print("\nAll paths:")
    for path in paths:
        print(path)


if __name__ == '__main__':
    main()