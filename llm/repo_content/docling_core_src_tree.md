#!base_path=/home/nicholasgrundl/projects/+forks/docling-core/docling_core
docling_core
├── cli
│   ├── __init__.py
│   └── view.py
├── resources
│   └── schemas
│       ├── doc
│       │   ├── ANN.json
│       │   ├── DOC.json
│       │   ├── OCR-output.json
│       │   └── RAW.json
│       ├── generated
│       │   ├── ccs_document_schema.json
│       │   └── minimal_document_schema_flat.json
│       └── search
│           ├── search_doc_mapping.json
│           └── search_doc_mapping_v2.json
├── search
│   ├── __init__.py
│   ├── json_schema_to_search_mapper.py
│   ├── mapping.py
│   ├── meta.py
│   └── package.py
├── transforms
│   ├── chunker
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── hierarchical_chunker.py
│   │   └── hybrid_chunker.py
│   └── __init__.py
├── types
│   ├── doc
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── document.py
│   │   ├── labels.py
│   │   ├── tokens.py
│   │   └── utils.py
│   ├── gen
│   │   ├── __init__.py
│   │   └── generic.py
│   ├── io
│   │   └── __init__.py
│   ├── legacy_doc
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── doc_ann.py
│   │   ├── doc_ocr.py
│   │   ├── doc_raw.py
│   │   ├── document.py
│   │   └── tokens.py
│   ├── nlp
│   │   ├── __init__.py
│   │   ├── qa.py
│   │   └── qa_labels.py
│   ├── rec
│   │   ├── __init__.py
│   │   ├── attribute.py
│   │   ├── base.py
│   │   ├── predicate.py
│   │   ├── record.py
│   │   ├── statement.py
│   │   └── subject.py
│   ├── __init__.py
│   └── base.py
├── utils
│   ├── __init__.py
│   ├── alias.py
│   ├── file.py
│   ├── generate_docs.py
│   ├── generate_jsonschema.py
│   ├── legacy.py
│   ├── validate.py
│   └── validators.py
├── __init__.py
└── py.typed