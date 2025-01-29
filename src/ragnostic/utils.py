"""
Basic utilities for document ID generation and file operations.
"""
from dataclasses import dataclass
import string
from pathlib import Path
from shutil import copy2
from typing import Optional

from nanoid import generate

DEFAULT_ALPHABET = string.ascii_lowercase + string.digits  # 0-9a-z

@dataclass
class FileOperationResult:
    """
    Result of a file operation containing success status and relevant details.
    
    Attributes:
        success: Whether the operation succeeded
        filepath: Path to the resulting file if successful
        error: Exception object if an error occurred
        error_code: String code indicating the type of error
    """
    success: bool
    filepath: Optional[Path] = None
    error: Optional[Exception] = None
    error_code: Optional[str] = None


def create_doc_id(prefix: str = "DOC", size: int = 12, alphabet: str = DEFAULT_ALPHABET) -> str:
    """
    Create a new document ID with optional prefix.
    
    Args:
        prefix: String prefix for the ID (default: "DOC")
        size: Length of the random portion (default: 12)
        alphabet: String of characters to use for ID generation (default: numbers and lowercase letters)
    
    Returns:
        Document ID string in format {prefix}_{random string}
    
    Example:
        >>> create_doc_id("PDF")
        'PDF_x1y2z3a4b5c6'
    """
    random_id = generate(alphabet=alphabet, size=size)
    return f"{prefix}_{random_id}"

def copy_file(src_path: str | Path, dest_dir: str | Path) -> FileOperationResult:
    """
    Copy a file to destination directory.
    
    Args:
        src_path: Source file path
        dest_dir: Destination directory
        
    Returns:
        FileOperationResult containing success status and details
        
    Example:
        >>> result = copy_file('documents/test.pdf', 'archive/')
        >>> if result.success:
        ...     print(f"File copied to {result.filepath}")
        ... else:
        ...     print(f"Copy failed: {result.error_code}")
    """
    src_path = Path(src_path)
    dest_dir = Path(dest_dir)
    
    # Check source file
    if not src_path.is_file():
        return FileOperationResult(
            success=False,
            error=FileNotFoundError(f"Source file not found: {src_path}"),
            error_code="SOURCE_NOT_FOUND"
        )
    
    # Check destination directory
    if not dest_dir.is_dir():
        return FileOperationResult(
            success=False,
            error=NotADirectoryError(f"Destination is not a directory: {dest_dir}"),
            error_code="INVALID_DESTINATION"
        )
        
    try:
        # Copy file preserving metadata
        new_path = dest_dir / src_path.name
        copy2(src_path, new_path)
        return FileOperationResult(success=True, filepath=new_path)
        
    except PermissionError as e:
        return FileOperationResult(
            success=False,
            error=e,
            error_code="PERMISSION_DENIED"
        )
    except OSError as e:
        return FileOperationResult(
            success=False,
            error=e,
            error_code="COPY_FAILED"
        )

def rename_file(file_path: str | Path, new_name: str) -> FileOperationResult:
    """
    Rename a file in its current directory.
    
    Args:
        file_path: Path to file to rename
        new_name: New filename (not path)
        
    Returns:
        FileOperationResult containing success status and details
        
    Example:
        >>> result = rename_file('archive/old.pdf', 'new.pdf')
        >>> if result.success:
        ...     print(f"File renamed to {result.filepath}")
        ... else:
        ...     print(f"Rename failed: {result.error_code}")
    """
    file_path = Path(file_path)
    
    # Check source file
    if not file_path.is_file():
        return FileOperationResult(
            success=False,
            error=FileNotFoundError(f"File not found: {file_path}"),
            error_code="FILE_NOT_FOUND"
        )
        
    try:
        new_path = file_path.parent / new_name
        file_path.rename(new_path)
        return FileOperationResult(success=True, filepath=new_path)
        
    except PermissionError as e:
        return FileOperationResult(
            success=False,
            error=e,
            error_code="PERMISSION_DENIED"
        )
    except OSError as e:
        return FileOperationResult(
            success=False,
            error=e,
            error_code="RENAME_FAILED"
        )