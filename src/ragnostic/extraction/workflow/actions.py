import pathlib
from burr.core import State, action, ApplicationBuilder
from burr.core import when

from ragnostic import utils

@action(reads=[], writes=["document_kind"])
def document_router(state: State, doc_id: str, db_connection) -> State:
    """Determine how to process the doc"""

    # Determine how to process the doc id based on the library entry
    # - Is it a PDF or a HTML?
    # - has it already been processed before?

    #Design Choices:
    # - should we load the document here or later?
    # - if loaded should we store it in the state as a python object?
    return state.update(document_kind='pdf')

@action(reads=[], writes=[])
def text_extraction(state: State, db_connection) -> State:
    """extract text"""
    # Extract text from pdf
    # - use the docling parser
    # - grab the raw text as is initially

    # Design Choices:
    # - should we store the docling parsed object in state and run various extraction steps on it?
    return state

@action(reads=[], writes=[])
def image_extraction(state: State, db_connection) -> State:
    """extract image"""

    # Extract and add images to database
    # - take docling object and put images with their metadata in the database
    
    # Design Choices:
    # - what inputs do we need? the docling objkect? the doc id and load it from database?
    
    return state

@action(reads=[], writes=[])
def table_extraction(state: State, db_connection) -> State:
    """extract table"""
    # Extract and add tables to database
    # - take docling object and put tables with their metadata in the database
    
    # Design Choices:
    # - what inputs do we need? the docling object? the doc id and load it from database?
    
    return state

@action(reads=[], writes=[])
def wikipedia_extraction(state: State, db_connection) -> State:
    """extract wikipedia"""

    # Design choices
    # Should we grab the HTML and store it then parse?
    # - should we just use the wikipedia API?
    # - should we do an image step later as well? 
    # - how would we identify images?
    return state

@action(reads=[], writes=[])
def metadata_extraction(state: State, db_connection) -> State:
    """extract table"""

    # Compile the metadata based on the previous steps
    # - does it have images, tables, etc?
    # - how many pages, etc
    # - status updates on the steps, flags, etc.
    
    return state
    
# Build and visualize graph/logic
(
    ApplicationBuilder()
    .with_actions(
        route=document_router, 
        pdf_text=text_extraction, 
        pdf_image=image_extraction, 
        pdf_table=table_extraction,
        pdf_metadata=metadata_extraction,
        wiki_extraction=wikipedia_extraction,
    )
    .with_transitions(
        ("route", "pdf_text", when(document_kind='pdf')),
        ("pdf_text", "pdf_image"),
        ("pdf_image", "pdf_table"),
        ("pdf_table", "pdf_metadata"),
        ("route", "wiki_extraction", ~when(document_kind='pdf')),
        ("wiki_extraction", "pdf_metadata"),
    )
    .with_entrypoint("route")
    .build()
)