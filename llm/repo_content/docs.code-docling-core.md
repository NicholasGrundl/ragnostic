# docling-core Package Summary

`docling-core` is a Python package designed for handling and processing structured document data.  It provides data models, utilities, and command-line tools for working with document representations, particularly focusing on metadata, search indexing, and data transformations.  The package is heavily reliant on Pydantic for data validation and type hinting, and leverages other libraries like `typer` for CLI creation and `jsonschema` for schema validation.

## Core Functionality

The package's main functions revolve around:

1. **Document Representation:**  Defines rich data models (`DoclingDocument`, `Record`, `Generic`) to represent documents with nested structures, metadata, provenance information, and associated data like images and tables.  These models utilize Pydantic for robust data validation and serialization.

2. **Search Indexing:** Provides tools and models (`JsonSchemaToSearchMapper`, `mapping.py`, `meta.py`, `package.py`) to map document schemas to search database schemas (e.g., Elasticsearch).  This facilitates efficient search and retrieval of documents based on their content and metadata.

3. **Data Transformations:** Includes data transformation functionalities, specifically a chunking mechanism (`transforms/chunker`) to divide documents into smaller, manageable units for further processing (e.g., LLM input).  Different chunking strategies (hierarchical and hybrid) are offered.

4. **CLI Tool:** A command-line interface (`cli/view.py`) is provided to view Docling JSON files in a web browser.

5. **Utilities:** Offers various helper functions and modules (`utils`) for tasks such as resolving file paths (local and remote), generating JSON Schema documentation from Pydantic models, and performing legacy data conversions.


## Key Classes and Modules

* **`docling_core.types.doc.DoclingDocument`:** The central class representing a structured document.  It includes methods for adding various types of content (text, tables, images), managing hierarchical relationships, and exporting the document in different formats (JSON, Markdown, HTML).

* **`docling_core.types.doc.TextItem`, `docling_core.types.doc.TableItem`, `docling_core.types.doc.PictureItem`:** Subclasses of `DocItem`, representing specific document elements.

* **`docling_core.types.rec.Record`:** A model for representing structured records with attributes, subjects, and provenance information.

* **`docling_core.types.gen.Generic`:** A generic model for unstructured document data.

* **`docling_core.search.JsonSchemaToSearchMapper`:** Converts JSON Schemas into search database schemas.

* **`docling_core.transforms.chunker.HierarchicalChunker`, `docling_core.transforms.chunker.HybridChunker`:** Implement different chunking strategies for document processing.

* **`docling_core.utils.file`:** Contains functions for resolving file sources (local paths and URLs).

* **`docling_core.utils.legacy`:** Provides utilities for converting between legacy and current document formats.


## Usage Examples

**CLI for viewing a Docling document:**

```bash
docling view path/to/your/document.json
```

**Resolving a file path:**

```python
from docling_core.utils.file import resolve_source_to_path
path = resolve_source_to_path("http://example.com/document.json")  # Or a local path
print(path)
```

**Chunking a document:**

```python
from docling_core.transforms.chunker import HybridChunker
from docling_core.types.doc import DoclingDocument  # Assuming you have a DoclingDocument object

chunker = HybridChunker()
for chunk in chunker.chunk(doc):
    print(chunk.text)
    print(chunk.meta)
```

## Notable Features

* **Rich Data Models:** Comprehensive data models ensure data integrity and consistency.
* **Data Validation:** Pydantic's validation capabilities guarantee data quality.
* **Extensible Design:**  The modular design allows for easy extension and customization.
* **Schema-Driven Search Indexing:**  Simplifies the process of creating search indexes.
* **Flexible Chunking:**  Supports various chunking strategies tailored to different needs.
* **Legacy Data Support:**  Includes tools for handling legacy data formats.


## Dependencies

* Python 3.8+
* Pydantic
* Typer
* jsonschema
* requests
* Pillow (PIL)
* pandas
* PyYAML
* latex2mathml
* tabulate  (optional, for Markdown export)
* sentence-transformers, transformers (optional, for HybridChunker)
* semchunk (optional, for HybridChunker)


This summary provides a high-level overview of the `docling-core` package. For detailed usage instructions and API specifications, refer to the package documentation.