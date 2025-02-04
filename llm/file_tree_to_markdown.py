#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Optional


def parse_tree_file(tree_file: Path) -> tuple[Path, List[str]]:
    """Parse a tree-structure file and extract base path and file paths.
    
    The function handles tree files with the following format:
    #!base_path=/path/to/base
    folder1
    ├── file1.txt
    ├── subfolder
    │   ├── file2.txt
    │   └── file3.txt
    └── file4.txt
    
    Args:
        tree_file: Path to the file containing the tree structure
        
    Returns:
        Tuple of (base_path, list of relative file paths)
        
    Raises:
        ValueError: If no base path is found or file structure is invalid
    """
    # Initialize tracking variables
    paths: List[str] = []           # List to store all file paths
    current_dirs: List[str] = []    # Stack to track current directory path
    base_path: Optional[Path] = None
    prev_level = 0                  # Track previous line's indentation level
    
    with open(tree_file) as f:
        for line_num, line in enumerate(f, 1):
            # Clean the line
            line = line.rstrip('\n')
            
            # Handle base path declaration
            if line.startswith("#!base_path="):
                if base_path is not None:
                    raise ValueError(f"Multiple base path declarations found at line {line_num}")
                try:
                    base_path = Path(line.split("=", 1)[1]).resolve()
                    continue
                except Exception as e:
                    raise ValueError(f"Invalid base path at line {line_num}: {str(e)}")
            
            # Skip empty lines and purely decorative tree lines
            if not line.strip() or line.strip() in ['├──', '└──', '│']:
                continue
            
            try:
                # Parse the line structure
                raw_prefix = line.split("─ ")[0] if "─ " in line else line
                name = line.split("─ ")[-1].strip() if "─ " in line else line.strip()
                
                # Calculate indentation level
                # Each level is typically 4 spaces (│   ) or similar
                indent = len(raw_prefix)
                level = indent // 4
                
                # Validate level change
                level_diff = prev_level - level
                # if level > prev_level + 1:
                #     raise ValueError(
                #         f"Invalid indentation at line {line_num}: "
                #         f"Can't increase more than one level at once"
                #     )
                
                # Determine if item is a directory
                # Consider it a directory if it has no extension or is a hidden folder
                is_dir = ('.' not in name) or (name.startswith('.') and '/' not in name)
                
                if is_dir:
                    # Handle directory entries
                    if level_diff > 0:  # Moving up in the tree
                        current_dirs = current_dirs[:-level_diff]
                    current_dirs = current_dirs[:level]  # Trim to current level
                    current_dirs.append(name)
                else:
                    # Handle file entries
                    if level_diff > 0:  # Moving up in the tree
                        current_dirs = current_dirs[:-level_diff]
                    current_dirs = current_dirs[:level]  # Trim to current level
                    
                    # Construct the relative path
                    full_path = str(Path().joinpath(*current_dirs) / name)
                    if full_path not in paths:  # Avoid duplicates
                        paths.append(full_path)
                
                prev_level = level
                
            except Exception as e:
                raise ValueError(
                    f"Error parsing line {line_num}: '{line}'\n"
                    f"Error: {str(e)}"
                )
    
    if base_path is None:
        raise ValueError("No base path declaration found in tree file")
    
    # Sort paths for consistent output
    paths.sort()
    
    return base_path, paths


def generate_markdown(
    tree_file: Path,
    output_file: Path | None,
    exclude_suffixes: Optional[List[str]] = None,
    exclude_filenames: Optional[List[str]] = None
) -> None:
    """Generate a markdown file containing the contents of all files in the tree.
    
    Args:
        tree_file: Path to the file containing the tree structure
        output_file: (optional) Path where to write the markdown output. Otherwise text
        exclude_suffixes: List of file suffixes to exclude
        exclude_filenames: List of filenames to exclude
    """
    
    # Determine the language for syntax highlighting
    lang = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.md': 'markdown',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.sh': 'bash',
        '.ipynb': 'json',
        '.html': 'html',
        '.css': 'css',
    }
    plaintext_extensions: set[str] = set(lang.keys())
    

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
    output_content = []

    for idx, file_path in enumerate(file_paths, start=1):
        # Convert to Path object and ensure unix-style path string
        abs_path = Path(base_path) / file_path

        # Create markdown entry header
        output_content.append(f"<file_{idx}>")
        output_content.append(f"<path>{file_path}</path>")

        output_content.append("<content>")
        # Process file content based on extension
        if abs_path.suffix.lower() in plaintext_extensions:
            suffix = Path(abs_path).suffix
            code_lang = lang.get(suffix, '')
            try:
                with abs_path.open('r', encoding='utf-8') as f:
                    content = f.read()
                output_content.append(f"```{code_lang}")
                output_content.append(content)
                output_content.append("```")
            except Exception as e:
                output_content.append(
                    f"\nError reading file: {str(e)}"
                )
        else:
            output_content.append(
                "\n[Content not displayed - Non-plaintext file]"
            )
        output_content.append("</content>")
        output_content.append(f"</file_{idx}>\n")


    if output_file is None:
        # Just print to screen
        return '\n'.join(output_content)
    
    # Write to output file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as f:
        f.write('\n'.join(output_content))
    return None




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
        default=None,
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
            output_file=Path(args.output) if args.output is not None else None,
            exclude_suffixes=args.exclude_suffixes,
            exclude_filenames=args.exclude_filenames
        )
    except Exception as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
