#!base_path=/home/nicholasgrundl/projects/ragnostic

├── docs
│   ├── 1_System_Requirements.md
│   ├── 2_Ragnostic_Project_Plan.md
│   ├── 2a_Document_Ingestion.md
│   └── 2b_Semantic_Extraction.md
├── llm
│   ├── artifacts
│   │   ├── Evaluation System Technical Specification.md
│   │   ├── Query Pipeline Technical Specification.md
│   │   ├── Vector Storage Technical Specification.md
│   │   └── system_prompt.md
│   ├── context
│   │   ├── file_content.md
│   │   ├── file_tree.md
│   │   └── repo_tree.md
│   ├── file_tree.py
│   └── file_tree_to_markdown.py
├── notebooks
│   ├── filetree_context_creation
│   ├── pdf_parsing_exploration
│   │   ├── ABOUT.md
│   │   ├── docling-exploration.ipynb
│   │   ├── macos-article-anthropic.md
│   │   ├── macos-article-haiku.md
│   │   ├── macos-article-openai.md
│   │   ├── macos-exploration.ipynb
│   │   ├── macos-journal-gemini.md
│   │   ├── macos-journal-haiku.md
│   │   ├── macos-journal-openai.md
│   │   ├── macos-report-haiku.md
│   │   ├── macos-report-openai.md
│   │   ├── macos-textbook-gemini.md
│   │   ├── macos-textbook-haiku.md
│   │   ├── macos-textbook-openai.md
│   │   ├── markerpdf-exploration.ipynb
│   │   ├── package-exploration.ipynb
│   │   ├── thebeast-article-docling.md
│   │   ├── thebeast-article-marker.md
│   │   ├── thebeast-journal-docling.md
│   │   ├── thebeast-journal-marker.md
│   │   ├── thebeast-report-docling.md
│   │   ├── thebeast-report-marker.md
│   │   ├── thebeast-textbook-docling.md
│   │   └── thebeast-textbook-marker.md
│   ├── document-ingestion.ipynb
│   └── filetree.ipynb
├── src
│   └── ragnostic
│       ├── db
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── models.py
│       │   └── schema.py
│       ├── ingestion
│       │   ├── validation
│       │   │   ├── __init__.py
│       │   │   ├── checks.py
│       │   │   ├── schema.py
│       │   │   └── validator.py
│       │   ├── __init__.py
│       │   ├── monitor.py
│       │   └── schema.py
│       ├── __init__.py
│       ├── dag_ingestion.py
│       └── utils.py
├── tests
│   ├── ingestion
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_checks.py
│   │   ├── test_schema.py
│   │   └── test_validator.py
│   ├── test_db.py
│   └── test_ingestion_monitor.py
├── .env.template
├── .gitignore
├── LICENSE
├── Makefile
├── README.md
├── action_items.md
├── pyproject.toml
├── requirements-dev.txt
├── requirements.txt
├── test.md
└── test.py