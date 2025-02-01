# Project Source Code

Base path: `/home/nicholasgrundl/projects/ragnostic`

## Root Directory

### 1_System_Requirements.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/1_System_Requirements.md*

### 2_Ragnostic_Project_Plan.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/2_Ragnostic_Project_Plan.md*

### 2a_Document_Ingestion.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/2a_Document_Ingestion.md*

### 2b_Semantic_Extraction.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/2b_Semantic_Extraction.md*

### ABOUT-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/ABOUT-checkpoint.md*

### ABOUT.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/ABOUT.md*

### Development-checkpoint.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/Development-checkpoint.ipynb*

### Evaluation System Technical Specification.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/Evaluation System Technical Specification.md*

### Query Pipeline Technical Specification.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/Query Pipeline Technical Specification.md*

### README.md

```markdown
# Background

This repo is to explore and implement RAG for consulting and technical applications that use heavy PDFs.

# MVP 1:

We will be focusing on an initial MVP to pipe asll the parts of the RAG system together for demoing and exploration as we build.

The main blocks are:

1. Raw document ingestion and storage
2. Document text extraction and labeling
3. Chunking and embedding in vector store
4. Query retrival
5. Evaluations

## Raw Document ingestion and storage

- collect and assemble raw documents to work with
- collect and assemble wikipedia articles to work with
- store documents in a database as blobs

## Document text extraction and labeling

- test various PDF readers and text extraction
- test wikipedia text semantics
- data model objects for documents with metadata
- document summarization for heirarchal RAG and text search
- document labeling based on summaries and metadata classification?


# Resources

We plan to look into the following for PDF reading and extraction:

OpenSource:
- PyMuPDF4LLM: https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/
- zerox: https://github.com/getomni-ai/zerox
- marker: https://github.com/VikParuchuri/marker
- docling: https://github.com/DS4SD/docling
- llmsherpa: https://github.com/nlmatics/llmsherpa

ClosedSource:
- llamaparse: https://github.com/run-llama/llama_parse
- unstructured: https://github.com/Unstructured-IO/unstructured
- llmwhisperer: https://github.com/Zipstack/unstract
- google document AI: https://cloud.google.com/python/docs/reference/documentai/latest

We plan to also use the internet for gap filling:

DataSources:
- wikipedia-api (more granular and updated): https://github.com/martin-majlis/Wikipedia-API
- wikipedia (higher level and stale): https://github.com/goldsmith/Wikipedia

Search:
- BraveAPI: https://api.search.brave.com/app/documentation/web-search/get-started
- BraveAPI python client (sync and async, stable): https://github.com/kayvane1/brave-api
- Brave python client alternative(async and uv/docker images): https://github.com/helmut-hoffer-von-ankershoffen/brave-search-python-client


# Installation of packages

## Python version
We require >=3.11

## Installation

The packages are a bit finnicky and some non python packages are required. Due to the pytorch requirement thigns are VERY paltform specific...
- CPU
- GPU
- OS

## MacOS Intel

> Due to pytorch versions being old on intel macOS i didnt get the marker pdf to run. Ill try it again on my WSL beast and see what happends.

1. poppler: image analysis
    - `brew install poppler`

2. Pytorch: CPU or GPU depending on machine
    - `uv add torch torchvision`
    > You may need to install an explicit CPU version, in that case:
    > `uv pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.0 torchvision==0.16.0`

3. PDF extraction packages
    - `uv add pymupdf4llm`
    - `uv add py-zerox`
    > marker-pdf is an early unstable version on mac intel
    > docling for intel mac with pinned pytorch is incompatible

4. Web search and wikipedia
   - `uv add brave-search`
   - `uv add wikipedia wikipedia-api`

5. Workflows and DAGs
   - `uv add burr[start]`

6. Indexing
   - `uv add llama_index`

## Ubuntu Intel + GPU

We are going to go the more stable and classic route of conda and pip

1. Setup a new miniconda env

2. Install the OS specific packages (mostly OCR)
    a. poppler: image analysis
    - `conda install -c conda-forge poppler`
    b. Tesseract
    - `conda install -c conda-forge tesseract`
    c. graphviz
    - `conda install graphviz`

3. Install CUDA (if GPU enabled)
    a. Install CUDA on WSL
    - https://docs.nvidia.com/cuda/wsl-user-guide/index.html#getting-started-with-cuda-on-wsl-2
    b. Add to `.bashrc`
    ```export PATH=/usr/local/cuda-12.8/bin${PATH:+:${PATH}}
    export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
    ```

4. Pytorch: CPU or GPU depending on machine
    - see: https://pytorch.org/get-started/locally/
    - in the conda env: `pip install torch torchvision torchaudio`
    - verify the installation
        ```
        import torch
        x = torch.rand(5, 3)
        print(x)
        torch.cuda.is_available()
        ```
        
5. Install packages and dev packages
    a. Use the Makefile routine
    - `make install`
    b. Alternatively use the requiremetns files
    - `requirements.txt`
    - `requirements-dev.txt`


## Envrionment Vars

1. NVIDIA/CUDA/Torch related
    a. specify GPU architecture
    - check with: ``
    - for TheBeast: `export TORCH_CUDA_ARCH_LIST="8.6"````

### Vector Storage Technical Specification.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/Vector Storage Technical Specification.md*

### __init__.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/__init__.py*

### action_items.md

```markdown
# Action Items

## consolidate scoping 
- remake sequyice diagrams and database data model diagrams
- claude docs into one
- map out tasks and sequence diagram and component diagram
- send to jesse lou
  - for review
- estimate time and complexity for each task
  - where contrasctors and interns could help
  - where to delegate effort

- timeline
  - meet next week friday again
- spend
  - track infraspend
  
- sign NDA?

## repo privacy or public discussion
- ragnostic for pipeline
- where to store data
  - local private first
  - s3 like later
- where to store eval set
  - local csv or database initially```

### article-docling-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/article-docling-checkpoint.md*

### checks.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/checks.py*

### client.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/client.py*

### conftest.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/conftest.py*

### dag_ingestion.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/dag_ingestion.py*

### docling-exploration-checkpoint.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/docling-exploration-checkpoint.ipynb*

### docling-exploration.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/docling-exploration.ipynb*

### document-ingestion-checkpoint.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/document-ingestion-checkpoint.ipynb*

### document-ingestion.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/document-ingestion.ipynb*

### file_tree.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/file_tree.py*

### file_tree_to_markdown.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/file_tree_to_markdown.py*

### journal-docling-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/journal-docling-checkpoint.md*

### macos-article-anthropic.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-article-anthropic.md*

### macos-article-haiku.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-article-haiku.md*

### macos-article-openai.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-article-openai.md*

### macos-exploration-checkpoint.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-exploration-checkpoint.ipynb*

### macos-exploration.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-exploration.ipynb*

### macos-journal-gemini.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-journal-gemini.md*

### macos-journal-haiku.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-journal-haiku.md*

### macos-journal-openai.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-journal-openai.md*

### macos-report-haiku.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-report-haiku.md*

### macos-report-openai.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-report-openai.md*

### macos-textbook-gemini.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-textbook-gemini.md*

### macos-textbook-haiku.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-textbook-haiku.md*

### macos-textbook-openai.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/macos-textbook-openai.md*

### markerpdf-exploration-checkpoint.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/markerpdf-exploration-checkpoint.ipynb*

### markerpdf-exploration.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/markerpdf-exploration.ipynb*

### models.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/models.py*

### monitor.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/monitor.py*

### package-exploration.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/package-exploration.ipynb*

### pyproject.toml

```
[project]
name = "ragnostic"
version = "0.1.0"
description = "Diagnostic RAG system for chemical process design and techno-economic analysis"
readme = "README.md"
authors = [
    { name = "Nicholas Grundl", email = "nicholasgrundl@gmail.com" }
]
requires-python = ">=3.11"
dependencies = [
]

[project.scripts]
ragnostic = "ragnostic:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = []
```

### report-docling-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/report-docling-checkpoint.md*

### report-marker-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/report-marker-checkpoint.md*

### requirements-dev.txt

```
# Interactive Development
jupyterlab
ipywidgets
wat

#Unit Testing
pytest
pytest-cov

# Formatting/Linting
mypy
ruff

#editable
-e .```

### requirements.txt

```
# General
python-magic

#Pytorch
torch
torchvision
torchaudio

#PDF Parsing
docling
marker-pdf
pymupdf4llm

#Internet Search
brave-search
wikipedia
wikipedia-api

#Database/Storage
sqlalchemy
pydantic
chromadb
nanoid

#ML/Data
numpy
pandas
scikit-learn

# Embeddings/LLMs
tiktoken
sentence-transformers
openai
cohere
anthropic
instructor

# Orchestration
burr[start]
sf-hamilton[visualization]

#Image manipulation
Pillow

```

### schema.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/schema.py*

### system_prompt.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/system_prompt.md*

### test.md

```markdown
#!base_path=/home/nicholasgrundl/projects/ragnostic/
src
└── ragnostic
    ├── db
    │   ├── __init__.py
    │   ├── client.py
    │   ├── models.py
    │   └── schema.py
    ├── ingestion
    │   ├── validation
    │   │   ├── __init__.py
    │   │   ├── checks.py
    │   │   ├── schema.py
    │   │   └── validator.py
    │   ├── __init__.py
    │   ├── monitor.py
    │   └── schema.py
    ├── __init__.py
    ├── dag_ingestion.py
    └── utils.py
```

### test.py

```python
#!/usr/bin/env python3
"""Parse markdown tree structure and return full file paths."""

import re
from pathlib import Path
from typing import List


def parse_tree_structure(markdown_text: str) -> tuple[str, List[str]]:
    """
    Parse markdown tree structure and return base path and all file paths.
    
    Args:
        markdown_text: String containing markdown tree structure
    
    Returns:
        Tuple containing base path and list of file paths (excluding directories)
    """
    # Extract base path from first line if present
    lines = markdown_text.strip().split('\n')
    base_path = ''
    start_idx = 0
    
    if lines[0].startswith('#!base_path='):
        base_path = lines[0].split('=')[1].strip()
        start_idx = 1
    
    paths = []
    current_path_components = []
    last_depth = -1
    
    for line in lines[start_idx:]:
        if not line.strip() or '│' in line:
            continue
            
        # Count the depth based on the number of spaces
        indent_match = re.match(r'^(\s*)[└├]──\s+(.+)$', line)
        if not indent_match:
            # Handle root directory case
            if not line.startswith(' '):
                current_path_components = [line.strip()]
            continue
            
        indent, name = indent_match.groups()
        depth = len(indent) // 4  # Assuming 4 spaces per level
        
        # Adjust the path components based on depth
        if depth <= last_depth:
            current_path_components = current_path_components[:depth]
        
        current_path_components.append(name)
        last_depth = depth
        
        # Only add paths that have a file extension (i.e., not directories)
        if '.' in name:
            paths.append(Path(*current_path_components))
    
    # Convert paths to strings and add base_path
    full_paths = [
        str(Path(base_path) / path) for path in paths
    ]
    
    return base_path, sorted(full_paths)

def main():
    """Main function to demonstrate usage."""
    # Example usage
    with open('test.md', 'r') as f:
        markdown_text = f.read()
    
    base_path, paths = parse_tree_structure(markdown_text)
    
    print(f"Base path: {base_path}")
    print("\nAll paths:")
    for path in paths:
        print(path)


if __name__ == '__main__':
    main()```

### test_checks.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/test_checks.py*

### test_db.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/test_db.py*

### test_ingestion_monitor.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/test_ingestion_monitor.py*

### test_schema.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/test_schema.py*

### test_source.md

```markdown
# Project Source Code

Base path: `/home/nicholasgrundl/projects/ragnostic`

## Root Directory

### 1_System_Requirements.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/1_System_Requirements.md*

### 2_Ragnostic_Project_Plan.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/2_Ragnostic_Project_Plan.md*

### 2a_Document_Ingestion.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/2a_Document_Ingestion.md*

### 2b_Semantic_Extraction.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/2b_Semantic_Extraction.md*

### ABOUT-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/ABOUT-checkpoint.md*

### ABOUT.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/ABOUT.md*

### Development-checkpoint.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/Development-checkpoint.ipynb*

### Evaluation System Technical Specification.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/Evaluation System Technical Specification.md*

### Query Pipeline Technical Specification.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/Query Pipeline Technical Specification.md*

### README.md

```markdown
# Background

This repo is to explore and implement RAG for consulting and technical applications that use heavy PDFs.

# MVP 1:

We will be focusing on an initial MVP to pipe asll the parts of the RAG system together for demoing and exploration as we build.

The main blocks are:

1. Raw document ingestion and storage
2. Document text extraction and labeling
3. Chunking and embedding in vector store
4. Query retrival
5. Evaluations

## Raw Document ingestion and storage

- collect and assemble raw documents to work with
- collect and assemble wikipedia articles to work with
- store documents in a database as blobs

## Document text extraction and labeling

- test various PDF readers and text extraction
- test wikipedia text semantics
- data model objects for documents with metadata
- document summarization for heirarchal RAG and text search
- document labeling based on summaries and metadata classification?


# Resources

We plan to look into the following for PDF reading and extraction:

OpenSource:
- PyMuPDF4LLM: https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/
- zerox: https://github.com/getomni-ai/zerox
- marker: https://github.com/VikParuchuri/marker
- docling: https://github.com/DS4SD/docling
- llmsherpa: https://github.com/nlmatics/llmsherpa

ClosedSource:
- llamaparse: https://github.com/run-llama/llama_parse
- unstructured: https://github.com/Unstructured-IO/unstructured
- llmwhisperer: https://github.com/Zipstack/unstract
- google document AI: https://cloud.google.com/python/docs/reference/documentai/latest

We plan to also use the internet for gap filling:

DataSources:
- wikipedia-api (more granular and updated): https://github.com/martin-majlis/Wikipedia-API
- wikipedia (higher level and stale): https://github.com/goldsmith/Wikipedia

Search:
- BraveAPI: https://api.search.brave.com/app/documentation/web-search/get-started
- BraveAPI python client (sync and async, stable): https://github.com/kayvane1/brave-api
- Brave python client alternative(async and uv/docker images): https://github.com/helmut-hoffer-von-ankershoffen/brave-search-python-client


# Installation of packages

## Python version
We require >=3.11

## Installation

The packages are a bit finnicky and some non python packages are required. Due to the pytorch requirement thigns are VERY paltform specific...
- CPU
- GPU
- OS

## MacOS Intel

> Due to pytorch versions being old on intel macOS i didnt get the marker pdf to run. Ill try it again on my WSL beast and see what happends.

1. poppler: image analysis
    - `brew install poppler`

2. Pytorch: CPU or GPU depending on machine
    - `uv add torch torchvision`
    > You may need to install an explicit CPU version, in that case:
    > `uv pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.0 torchvision==0.16.0`

3. PDF extraction packages
    - `uv add pymupdf4llm`
    - `uv add py-zerox`
    > marker-pdf is an early unstable version on mac intel
    > docling for intel mac with pinned pytorch is incompatible

4. Web search and wikipedia
   - `uv add brave-search`
   - `uv add wikipedia wikipedia-api`

5. Workflows and DAGs
   - `uv add burr[start]`

6. Indexing
   - `uv add llama_index`

## Ubuntu Intel + GPU

We are going to go the more stable and classic route of conda and pip

1. Setup a new miniconda env

2. Install the OS specific packages (mostly OCR)
    a. poppler: image analysis
    - `conda install -c conda-forge poppler`
    b. Tesseract
    - `conda install -c conda-forge tesseract`
    c. graphviz
    - `conda install graphviz`

3. Install CUDA (if GPU enabled)
    a. Install CUDA on WSL
    - https://docs.nvidia.com/cuda/wsl-user-guide/index.html#getting-started-with-cuda-on-wsl-2
    b. Add to `.bashrc`
    ```export PATH=/usr/local/cuda-12.8/bin${PATH:+:${PATH}}
    export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
    ```

4. Pytorch: CPU or GPU depending on machine
    - see: https://pytorch.org/get-started/locally/
    - in the conda env: `pip install torch torchvision torchaudio`
    - verify the installation
        ```
        import torch
        x = torch.rand(5, 3)
        print(x)
        torch.cuda.is_available()
        ```
        
5. Install packages and dev packages
    a. Use the Makefile routine
    - `make install`
    b. Alternatively use the requiremetns files
    - `requirements.txt`
    - `requirements-dev.txt`


## Envrionment Vars

1. NVIDIA/CUDA/Torch related
    a. specify GPU architecture
    - check with: ``
    - for TheBeast: `export TORCH_CUDA_ARCH_LIST="8.6"````

### Vector Storage Technical Specification.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/Vector Storage Technical Specification.md*

### __init__.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/__init__.py*

### action_items.md

```markdown
# Action Items

## consolidate scoping 
- remake sequyice diagrams and database data model diagrams
- claude docs into one
- map out tasks and sequence diagram and component diagram
- send to jesse lou
  - for review
- estimate time and complexity for each task
  - where contrasctors and interns could help
  - where to delegate effort

- timeline
  - meet next week friday again
- spend
  - track infraspend
  
- sign NDA?

## repo privacy or public discussion
- ragnostic for pipeline
- where to store data
  - local private first
  - s3 like later
- where to store eval set
  - local csv or database initially```

### article-docling-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/article-docling-checkpoint.md*

### checks.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/checks.py*

### client.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/client.py*

### conftest.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/conftest.py*

### dag_ingestion.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/dag_ingestion.py*

### docling-exploration-checkpoint.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/docling-exploration-checkpoint.ipynb*

### docling-exploration.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/docling-exploration.ipynb*

### document-ingestion-checkpoint.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/document-ingestion-checkpoint.ipynb*

### document-ingestion.ipynb

```
*File not found: /home/nicholasgrundl/projects/ragnostic/document-ingestion.ipynb*

### file_tree.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/file_tree.py*

### file_tree_to_markdown.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/file_tree_to_markdown.py*

### journal-docling-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/journal-docling-checkpoint.md*

```

### test_validator.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/test_validator.py*

### textbook-docling-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/textbook-docling-checkpoint.md*

### textbook-marker-checkpoint.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/textbook-marker-checkpoint.md*

### thebeast-article-docling.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/thebeast-article-docling.md*

### thebeast-article-marker.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/thebeast-article-marker.md*

### thebeast-journal-docling.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/thebeast-journal-docling.md*

### thebeast-journal-marker.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/thebeast-journal-marker.md*

### thebeast-report-docling.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/thebeast-report-docling.md*

### thebeast-report-marker.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/thebeast-report-marker.md*

### thebeast-textbook-docling.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/thebeast-textbook-docling.md*

### thebeast-textbook-marker.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/thebeast-textbook-marker.md*

### tree.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/tree.md*

### tree.txt

```
#!base_path=/home/nicholasgrundl/projects/ragnostic

├── data
│   ├── article
│   │   ├── BROCHURE_ContinuousCellCultureat2000L.pdf
│   │   └── REPORT_2003_OptimizePowerConsumptionInAerobicFermenters.pdf
│   ├── journal
│   │   └── JOURNAL_2017_AerationCostsInStirredTankAndBubbleColumnBioreactors.pdf
│   ├── report
│   │   ├── Humbird_20211004_REPORT_scaleup_economics_for_cultured_meat.pdf
│   │   ├── PEP_Report_211B_HYDROCRACKING OF HEAVY OILS AND RESIDUA.pdf
│   │   ├── PEP_Report_214A- Heavy Oil Hydrotreating.pdf
│   │   └── REPORT_ConsultancyOnLargeScaleSubmergedAerobicCultivationProcessDesignNRELGenomatica.pdf
│   └── textbook
│       ├── Ch51_Industrial_Crystallization.pdf
│       ├── ChE_Design_Towler_2008.pdf
│       ├── Crystallization_Ch11_StephenGlasgow_Fermentation_and_biochemical_engineering_handbook.pdf
│       ├── TEXT_1995_TetraPak_DairyProcessingHandbook.pdf
│       ├── TEXT_2008_CostEstimatingManualForWaterTreatmentFacilities.pdf
│       ├── TEXT_2010_ChemicalProcessEquipmentSelectionAndDesign.pdf
│       ├── TEXT_2015_BioProcessDesignAndEconomics.pdf
│       ├── TEXT_2016_Industrial_Scale_Fermentation.pdf
│       ├── TEXT_2021_ProteinProcessingInFoodAndBioproductManufacturing.pdf
│       └── TEXT_DairyProcessingHandbook_WheyProcessingChapter15.pdf
├── docs
│   ├── 1_System_Requirements.md
│   ├── 2_Ragnostic_Project_Plan.md
│   ├── 2a_Document_Ingestion.md
│   └── 2b_Semantic_Extraction.md
├── llm
│   ├── Evaluation System Technical Specification.md
│   ├── Query Pipeline Technical Specification.md
│   ├── Vector Storage Technical Specification.md
│   ├── file_tree.py
│   ├── file_tree_to_markdown.py
│   ├── system_prompt.md
│   ├── tree.md
│   └── tree_source.md
├── notebooks
│   ├── .ipynb_checkpoints
│   │   ├── Development-checkpoint.ipynb
│   │   ├── article-docling-checkpoint.md
│   │   ├── docling-exploration-checkpoint.ipynb
│   │   ├── document-ingestion-checkpoint.ipynb
│   │   ├── journal-docling-checkpoint.md
│   │   ├── markerpdf-exploration-checkpoint.ipynb
│   │   ├── report-docling-checkpoint.md
│   │   ├── report-marker-checkpoint.md
│   │   ├── test-checkpoint.jpg
│   │   ├── textbook-docling-checkpoint.md
│   │   └── textbook-marker-checkpoint.md
│   ├── pdf_parsing_exploration
│   │   ├── .ipynb_checkpoints
│   │   │   ├── ABOUT-checkpoint.md
│   │   │   └── macos-exploration-checkpoint.ipynb
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
│   └── document-ingestion.ipynb
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
├── .env
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
├── test.py
├── test_source.md
└── tree.txt
```

### tree_source.md

```markdown
*File not found: /home/nicholasgrundl/projects/ragnostic/tree_source.md*

### utils.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/utils.py*

### validator.py

```python
*File not found: /home/nicholasgrundl/projects/ragnostic/validator.py*

