import pathlib
from burr.core import ApplicationBuilder
from ragnostic import ingestion
from ragnostic import db

def build_ingestion_workflow(
    storage_dir: str = "./document_storage",
    db_path: str | None = None,
    max_file_size: int = 100 * 1024 * 1024,  # 100MB
    text_preview_chars: int = 1000
):
    """Build the document ingestion workflow application.
    
    Args:
        storage_dir: Directory to store processed documents
        db_path: Optional path to SQLite database. If None creates a new one
        max_file_size: Maximum allowed file size in bytes
        text_preview_chars: Number of characters for text preview
        
    Returns:
        Configured workflow application
    """
    # Ensure directories exist
    pathlib.Path(storage_dir).mkdir(parents=True, exist_ok=True)
    
    # Create database client
    db_url = db.create_sqlite_url(db_path)
    db_client = db.DatabaseClient(db_url)
    
    # Build workflow
    app = ApplicationBuilder()
    
    # Add monitor action
    app = app.with_actions(
        monitor=ingestion.monitor_action, 
        validation=ingestion.validation_action.bind(db_client=db_client,max_file_size=max_file_size),
        processing=ingestion.processing_action.bind(storage_dir=storage_dir), 
        indexing=ingestion.indexing_action.bind(db_client=db_client, text_preview_chars=text_preview_chars),
    )
    
    app = app.with_transitions(
        ("monitor", "validation"),
        ("validation", "processing"),
        ("processing", "indexing"),
    )
    
    app = app.with_entrypoint("monitor")

    return app.build()

def run_ingestion(ingest_dir = "./ingest", **kwargs):
    """Run the document ingestion workflow.
    
    Args:
        ingest_dir: Directory to monitor for new documents
        **kwargs: Additional arguments for build_ingestion_workflow
    """
    # Default args from environment
    storage_dir = kwargs.get('storage_dir', './storage')
    db_path = kwargs.get('db_path', None)
    max_file_size = kwargs.get('max_file_size', 100 * 1024 * 1024)  # 100MB
    text_preview_chars = kwargs.get('text_preview_chars', 1000)

    workflow = build_ingestion_workflow(
        storage_dir = storage_dir,
        db_path = db_path,
        max_file_size = max_file_size,
        text_preview_chars = text_preview_chars,
    )
    *_, state = workflow.run(
        halt_after=['indexing'],
        inputs={"ingest_dir": ingest_dir}
    )
    return state
