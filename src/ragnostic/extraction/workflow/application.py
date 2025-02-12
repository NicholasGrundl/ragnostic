import pathlib
from burr.core import ApplicationBuilder
from ragnostic import extraction
from ragnostic import db

def build_ingestion_workflow(
    config_path: str = "./config.yaml",
    db_path: str | None = None,
):
    """Build the document extraction workflow application.
    
    Args:
        config_path: PAth to configuration file
        db_path: Optional path to SQLite database. If None creates a new one
        
    Returns:
        Configured workflow application
    """
    
    # Create database client
    db_url = db.create_sqlite_url(db_path)
    db_client = db.DatabaseClient(db_url)
    
    # Build workflow
    app = ApplicationBuilder()
    
    # Add monitor action
    app = app.with_actions(
        converter_configure=extraction.converter_configure, 
        converter_run=extraction.converter_run.bind(db_client=db_client), 
        converter_handle=extraction.converter_handle, 
        converter_fail=extraction.converter_fail.bind(db_client=db_client),
        converter_success=extraction.converter_success.bind(db_client=db_client),
        extraction_run=extraction.extraction_run,
        extraction_store=extraction.extraction_store.bind(db_client=db_client),
        extraction_handle=extraction.extraction_handle,
        extraction_fail=extraction.extraction_fail.bind(db_client=db_client),
        extraction_success=extraction.extraction_success.bind(db_client=db_client),
    )
    
    app = app.with_transitions(
        ("converter_configure", "converter_run"),
        ("converter_run", "converter_handle"),
        ("converter_handle", "converter_fail", when(conversion_status='fail')),
        ("converter_handle", "converter_success", when(conversion_status='success')),
        ("converter_success", "extraction_run"),
        ("extraction_run", "extraction_store"),
        ("extraction_store", "extraction_handle"),
        ("extraction_handle", "extraction_fail", when(extraction_status='fail')),
        ("extraction_handle", "extraction_success", when(extraction_status='success')),
        
    )

    app = app.with_entrypoint("converter_configure")

    return app.build()


def run_extraction(document_id: str | None = None, **kwargs):
    """Run the document extraction workflow.
    
    Args:
        ingest_dir: Directory to monitor for new documents
        **kwargs: Additional arguments for build_ingestion_workflow
    """
    # Default args from environment
    storage_dir = kwargs.get('config_path', './config.yaml')
    db_path = kwargs.get('db_path', None)
    
    workflow = build_ingestion_workflow(**kwargs)
    *_, state = workflow.run(
        halt_after=['extraction_fail','extraction_success'],
        inputs={"document_id": document_id}
    )
    return state
