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
            line = line.rstrip('\n')

            # Parse header for base path
            if line.startswith("#!base_path="):
                prefix, _, base_path = line.partition("=")
                base_path = Path(base_path).resolve()
                continue
                
            # Skip empty lines and lines with just tree characters
            if not line.strip() or line.strip() in ['├──', '└──', '│']:
                continue

            # Count the actual indent level by looking at the tree characters
            prefix, _, name = line.partition("─ ")
            indent = len(prefix+_)
            level = indent // 4
            level_diff = prev_level - level
            
            if '.' not in name:
                is_dir = True
            else:
                is_dir = False
            
            if is_dir:
                # Update current_dirs
                if level_diff > 0: #rose up levels
                    current_dirs = current_dirs[:-level_diff]
                    current_dirs.append(name)
                elif level_diff < 0: #dropped down levels
                    current_dirs.append(name)
            else:
                # Update current_dirs
                if level_diff > 0: #rose up levels
                    current_dirs = current_dirs[:-level_diff]

                full_path = str(Path().joinpath(*current_dirs) / name)
                if full_path not in paths:  # Avoid duplicates
                        paths.append(full_path)

            prev_level = level
    
    if base_path is None:
        raise ValueError("No base path found in tree file")
        
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
