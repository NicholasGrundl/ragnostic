#!base_path=/home/nicholasgrundl/projects/ragnostic/src
src
└── ragnostic
    ├── db
    │   ├── __init__.py
    │   ├── client.py
    │   ├── models.py
    │   └── schema.py
    ├── ingestion
    │   ├── indexing
    │   │   ├── __init__.py
    │   │   ├── extraction.py
    │   │   ├── indexer.py
    │   │   └── schema.py
    │   ├── monitor
    │   │   ├── __init__.py
    │   │   ├── monitor.py
    │   │   └── schema.py
    │   ├── processor
    │   │   ├── __init__.py
    │   │   ├── processor.py
    │   │   ├── schema.py
    │   │   └── storage.py
    │   ├── validation
    │   │   ├── __init__.py
    │   │   ├── checks.py
    │   │   ├── schema.py
    │   │   └── validator.py
    │   ├── __init__.py
    │   └── utils.py
    ├── __init__.py
    └── dag_ingestion.py