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

3. Install CUDA (if GPU enabled)
    a. Install CUDA on WSL
    - https://docs.nvidia.com/cuda/wsl-user-guide/index.html#getting-started-with-cuda-on-wsl-2
    b. Add to `.bashrc`
    ```export PATH=/usr/local/cuda-12.8/bin${PATH:+:${PATH}}
    export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
    ```

3. Pytorch: CPU or GPU depending on machine
    - see: https://pytorch.org/get-started/locally/
    - in the conda env: `pip install torch torchvision torchaudio`
    - verify the installation
        ```
        import torch
        x = torch.rand(5, 3)
        print(x)
        torch.cuda.is_available()
        ```
        
4. Install packages and dev packages
    a. Use the Makefile routine
    - `make install`
    b. Alternatively use the requiremetns files
    - `requirements.txt`
    - `requirements-dev.txt`
