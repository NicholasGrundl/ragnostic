import pathlib
from burr.core import State, action

from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption, ConversionStatus
from docling.datamodel.document import ConversionResult

from ragnostic.db.client import DatabaseClient
from .. import configuration
from .. import extract_contents

@action(reads=[], writes=["config"])
def converter_configure(state: State, config_path: str | None = None) -> State:
    if config_path is None:
        #Pipeline
        pipeline_options = configuration.get_default_pipeline_configuration()
    else:
        # Configure from file/yaml
        raise NotImplementedError("File based pipeline config not yet available")

    return state.update(config=pipeline_options)

@action(reads=["config"], writes=["document_id", "conversion_document", "conversion_status"])
def converter_run(state: State, document_id: str, db_client: DatabaseClient,) -> State:
    
    # Load Document
    document = db_client.get_document_by_id(doc_id=document_id)
    document_filepath = document.raw_file_path


    # setup pipeline
    pipeline_options = state['config']
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )
    
    # convert document
    result = converter.convert(
        document_filepath,
        max_num_pages=100,  # Limit number of pages
        max_file_size=20971520  # Limit file size (20MB in this example)
    )

    # Check conversion status
    if result.status == ConversionStatus.SUCCESS:
        status = 'success'
    elif result.status == ConversionStatus.PARTIAL_SUCCESS:
        status = 'success'
    elif result.status == ConversionStatus.FAILURE:
        status='fail'
    else:
        status='fail'
    # update state decision variable
    if status=='fail':
        return state.update(
            document_id=document_id,
            conversion_document={},
            conversion_status=status
        )
    return state.update(
        document_id=document_id,
        conversion_document=result.document,
        conversion_status=status
    )

@action(reads=["conversion_status"], writes=["conversion_status"])
def converter_handle(state: State) -> State:
    """Handle conversion errors and status"""

    # TODO: redundant for now to manage serialization
    # Check conversion status
    status = state['conversion_status']
    
    # update state decision variable
    return state

@action(reads=["document_id", "conversion_status"], writes=[])
def converter_fail(state: State, db_client: DatabaseClient,) -> State:
    """Handle conversion failure"""
    # Update DB with info/status

    # Trigger notifications as needed
    
    return state

@action(reads=["document_id", "conversion_status"], writes=[])
def converter_success(state: State, db_client: DatabaseClient,) -> State:
    """Handle conversion success"""
    # Update DB with info/status

    # Trigger notifications as needed
    
    return state

@action(reads=["conversion_document"], writes=["extraction_content","extraction_status"])
def extraction_run(state: State) -> State:
    """Extract parts from the docling conversion"""
    doc = state['conversion_document']
    
    # Extract all parts    
    contents = extract_contents.extract_contents_from_doc(doc=doc)

    # update status as needed
    status = 'success'
    return state.update(extraction_content=contents,extraction_status=status)

@action(reads=["document_id","extraction_content"], writes=["extraction_status"])
def extraction_store(state: State, db_client: DatabaseClient,) -> State:
    """Store all items in db"""
    document_id = state['document_id']
    extraction_content = state['extraction_content']
    
    # Store in DB

    # Update status
    status = 'success'
    return state.update(extraction_status=status)
    

@action(reads=["extraction_content","extraction_status"], writes=["extraction_status"])
def extraction_handle(state: State) -> State:
    """Handle extraction errors and status"""
    # Check extraction status

    # update state decision variable
    return state

@action(reads=["document_id","extraction_status"], writes=[])
def extraction_fail(state: State, db_client: DatabaseClient,) -> State:
    """Handle extraction failure"""
    # Update DB with info/status

    # Trigger notifications as needed
    return state

@action(reads=["document_id","extraction_status"], writes=[])
def extraction_success(state: State, db_client: DatabaseClient) -> State:
    """Handle extraction success"""
    # Update DB with info/status

    # Trigger notifications as needed
    return state
    