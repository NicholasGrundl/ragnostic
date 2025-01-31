"""Individual validation checks for document ingestion."""
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Union
import magic

from ragnostic.db.client import DatabaseClient
from .schema import ValidationCheckType, ValidationCheckFailure


def compute_file_hash(filepath: Path) -> Optional[str]:
    """Compute SHA-256 hash of file."""
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None


def check_file_hash(filepath: Path) -> Union[str,ValidationCheckFailure]:
    """Compute SHA-256 hash of file.
    
    Returns:
        Tuple of (hash_value, check_failure). If successful, check_failure will be None.
    """
    hash_value = compute_file_hash(filepath)
    if hash_value is None:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.CORRUPTED_FILE,
            message="Unable to compute file hash"
        )
    return hash_value


def check_file_exists(filepath: Path) -> Union[bool, ValidationCheckFailure]:
    """Check if file exists and is a regular file."""
    if not filepath.exists() or not filepath.is_file():
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.OTHER,
            message="File does not exist or is not a regular file"
        )
    return True


def check_file_size(filepath: Path, max_size: int) -> Union[int, ValidationCheckFailure]:
    """Check if file size is within limits."""
    try:
        file_size = filepath.stat().st_size
    except Exception as e:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.PERMISSION_ERROR,
            message=f"Unable to check file size: {str(e)}"
        )
        
    if file_size > max_size:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.FILE_TOO_LARGE,
            message=f"File exceeds maximum size of {max_size} bytes",
            details={"file_size": file_size, "max_size": max_size}
        )
    return file_size
    

def check_mime_type(filepath: Path, supported_types: list[str]) -> Union[str, ValidationCheckFailure]:
    """Check if file mime type is supported."""
    try:
        mime_type = magic.from_file(str(filepath), mime=True)
        if mime_type not in supported_types:
            return ValidationCheckFailure(
                filepath=filepath,
                check_type=ValidationCheckType.INVALID_MIMETYPE,
                message=f"Unsupported mime type: {mime_type}",
                details={"mime_type": mime_type}
            )
    except Exception as e:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.OTHER,
            message=f"Unable to determine mime type: {str(e)}"
        )
    return mime_type
    

def check_hash_unique(filepath: Path, file_hash: str, db_client: DatabaseClient) -> Union[bool, ValidationCheckFailure]:
    """Check if file hash already exists in database."""
    existing_doc = db_client.get_document_by_hash(file_hash)
    if existing_doc:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.DUPLICATE_HASH,
            message="Document with same hash already exists",
            details={"existing_doc_id": existing_doc.id}
        )
    return True
