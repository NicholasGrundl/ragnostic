#!base_path=/home/nicholasgrundl/projects/+forks/docling/docling
docling
├── backend
│   ├── json
│   │   ├── __init__.py
│   │   └── docling_json_backend.py
│   ├── xml
│   │   ├── __init__.py
│   │   ├── pubmed_backend.py
│   │   └── uspto_backend.py
│   ├── __init__.py
│   ├── abstract_backend.py
│   ├── asciidoc_backend.py
│   ├── docling_parse_backend.py
│   ├── docling_parse_v2_backend.py
│   ├── html_backend.py
│   ├── md_backend.py
│   ├── msexcel_backend.py
│   ├── mspowerpoint_backend.py
│   ├── msword_backend.py
│   ├── pdf_backend.py
│   └── pypdfium2_backend.py
├── chunking
│   └── __init__.py
├── cli
│   ├── __init__.py
│   └── main.py
├── datamodel
│   ├── __init__.py
│   ├── base_models.py
│   ├── document.py
│   ├── pipeline_options.py
│   └── settings.py
├── models
│   ├── __init__.py
│   ├── base_model.py
│   ├── base_ocr_model.py
│   ├── code_formula_model.py
│   ├── document_picture_classifier.py
│   ├── ds_glm_model.py
│   ├── easyocr_model.py
│   ├── layout_model.py
│   ├── ocr_mac_model.py
│   ├── page_assemble_model.py
│   ├── page_preprocessing_model.py
│   ├── rapid_ocr_model.py
│   ├── table_structure_model.py
│   ├── tesseract_ocr_cli_model.py
│   └── tesseract_ocr_model.py
├── pipeline
│   ├── __init__.py
│   ├── base_pipeline.py
│   ├── simple_pipeline.py
│   └── standard_pdf_pipeline.py
├── utils
│   ├── __init__.py
│   ├── accelerator_utils.py
│   ├── export.py
│   ├── glm_utils.py
│   ├── layout_postprocessor.py
│   ├── ocr_utils.py
│   ├── profiling.py
│   ├── utils.py
│   └── visualization.py
├── __init__.py
├── document_converter.py
├── exceptions.py
└── py.typed