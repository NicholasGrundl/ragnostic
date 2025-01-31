# Project Source Code

Base path: `/home/nicholasgrundl/projects/ragnostic/src`

## ragnostic/__init__.py

```python
def main() -> None:
    print("Hello from ragnostic!")
```

## ragnostic/client.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/src/ragnostic/client.py*

## ragnostic/models.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/src/ragnostic/models.py*

## ragnostic/schema.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/src/ragnostic/schema.py*

## ragnostic/checks.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/src/ragnostic/checks.py*

## ragnostic/validator.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/src/ragnostic/validator.py*

## ragnostic/monitor.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/src/ragnostic/monitor.py*

## ragnostic/dag_ingestion.py

```python
import pathlib
from burr.core import State, action, ApplicationBuilder

from ragnostic import utils

@action(reads=[], writes=["ingestion_status","ingestion_filepaths"])
def monitor(state: State, ingest_dir: str) -> State:
    """Checks if directory has files to ingest"""
    file_paths = []
    # Check filepath is valid
    path = pathlib.Path(ingest_dir)
    if (path.exists()) and (path.is_dir()):
        for p in path.iterdir():
            if p.suffix in ['.PDF','.pdf']:
                file_paths.append(str(p.resolve()))
        ingestion_status = "ingesting"
    else:
        #log status error
        ingestion_status="completed"
    
    return state.update(
        ingestion_status=ingestion_status, 
        ingestion_filepaths=file_paths
    )

@action(reads=["ingestion_filepaths"], writes=["valid_filepaths","invalid_filepaths"])
def validation(state: State, db_connection:str) -> State:
    """Check which files in the ingestion list are valid
    - not duplicates, etc.
    """
    valid_filepaths = []
    invalid_filepaths = []

    for filepath in state.get("ingestion_filepaths"):
        # Check duplicates
        # check with hash against the database?
        # - other checks?
        is_valid=True

        #move to list
        if is_valid:
            valid_filepaths.append(filepath)
        else:
            invalid_filepaths.append(filepath)

    return state.update(
        valid_filepaths=valid_filepaths, 
        invalid_filepaths=invalid_filepaths,
    )


@action(reads=["valid_filepaths"], writes=["successful_docs","failed_docs"])
def ingestion(state: State, storage_dir: str) -> State:
    """Process a batch of documents, tracking successes and failures."""
    
    filepaths = state.get("valid_filepaths")
    successful = []
    failed = []
    
    for p in filepaths:
        
        # Move file to new location
        copy_result = utils.copy_file(src_path=p, dest_dir=storage_dir)
        if not copy_result.success:
            failed.append((p, copy_result.error_code))
            continue
        # Generate new document ID and filename
        doc_id = utils.create_doc_id(prefix="DOC")
        suffix = pathlib.Path(p).suffix
        doc_filename = f"{doc_id}{suffix}"
        # Rename with document ID
        rename_result = utils.rename_file(file_path=copy_result.filepath, new_name=doc_filename)
        if not rename_result.success:
            failed.append((rename_result.filepath, rename_result.error_code))
            continue
        successful.append(rename_result.filepath)
    
    return state.update(successful_docs=successful, failed_docs=failed)

@action(reads=["successful_docs"], writes=["ingestion_status"])
def indexing(state: State, db_connection: str) -> State:
    """Update database with succesfully ingested docs"""
    successful = state.get("successful_docs")

    # Update database with all document ids
    # - primary key is document id
    # - filepath is storage path
    # - should we add metadata here? put a status for further processing?
    ingestion_status = "Completed"
    return state.update(ingestion_status=ingestion_status)
```

## ragnostic/utils.py

```python
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
        )```

