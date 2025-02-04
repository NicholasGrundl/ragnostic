<file_1>
<path>assets/docling_arch.png</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_1>

<file_2>
<path>assets/docling_arch.pptx</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_2>

<file_3>
<path>assets/docling_doc_hierarchy_1.png</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_3>

<file_4>
<path>assets/docling_doc_hierarchy_2.png</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_4>

<file_5>
<path>assets/docling_ecosystem.png</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_5>

<file_6>
<path>assets/docling_ecosystem.pptx</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_6>

<file_7>
<path>assets/docling_processing.png</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_7>

<file_8>
<path>assets/logo.png</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_8>

<file_9>
<path>assets/logo.svg</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_9>

<file_10>
<path>concepts/architecture.md</path>
<content>
```markdown
![docling_architecture](../assets/docling_arch.png)

In a nutshell, Docling's architecture is outlined in the diagram above.

For each document format, the *document converter* knows which format-specific *backend* to employ for parsing the document and which *pipeline* to use for orchestrating the execution, along with any relevant *options*.

!!! tip

    While the document converter holds a default mapping, this configuration is parametrizable, so e.g. for the PDF format, different backends and different pipeline options can be used — see [Usage](../usage.md#adjust-pipeline-features).

The *conversion result* contains the [*Docling document*](./docling_document.md), Docling's fundamental document representation.

Some typical scenarios for using a Docling document include directly calling its *export methods*, such as for markdown, dictionary etc., or having it chunked by a [*chunker*](./chunking.md).

For more details on Docling's architecture, check out the [Docling Technical Report](https://arxiv.org/abs/2408.09869).

!!! note

    The components illustrated with dashed outline indicate base classes that can be subclassed for specialized implementations.

```
</content>
</file_10>

<file_11>
<path>concepts/chunking.md</path>
<content>
```markdown
## Introduction

A *chunker* is a Docling abstraction that, given a
[`DoclingDocument`](./docling_document.md), returns a stream of chunks, each of which
captures some part of the document as a string accompanied by respective metadata.

To enable both flexibility for downstream applications and out-of-the-box utility,
Docling defines a chunker class hierarchy, providing a base type, `BaseChunker`, as well
as specific subclasses.

Docling integration with gen AI frameworks like LlamaIndex is done using the
`BaseChunker` interface, so users can easily plug in any built-in, self-defined, or
third-party `BaseChunker` implementation.

## Base Chunker

The `BaseChunker` base class API defines that any chunker should provide the following:

- `def chunk(self, dl_doc: DoclingDocument, **kwargs) -> Iterator[BaseChunk]`:
  Returning the chunks for the provided document.
- `def serialize(self, chunk: BaseChunk) -> str`:
  Returning the potentially metadata-enriched serialization of the chunk, typically
  used to feed an embedding model (or generation model).

## Hybrid Chunker

!!! note "To access `HybridChunker`"

    - If you are using the `docling` package, you can import as follows:
        ```python
        from docling.chunking import HybridChunker
        ```
    - If you are only using the `docling-core` package, you must ensure to install
        the `chunking` extra, e.g.
        ```shell
        pip install 'docling-core[chunking]'
        ```
        and then you
        can import as follows:
        ```python
        from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
        ```

The `HybridChunker` implementation uses a hybrid approach, applying tokenization-aware
refinements on top of document-based [hierarchical](#hierarchical-chunker) chunking.

More precisely:

- it starts from the result of the hierarchical chunker and, based on the user-provided
  tokenizer (typically to be aligned to the embedding model tokenizer), it:
- does one pass where it splits chunks only when needed (i.e. oversized w.r.t.
tokens), &
- another pass where it merges chunks only when possible (i.e. undersized successive
chunks with same headings & captions) — users can opt out of this step via param
`merge_peers` (by default `True`)

👉 Example: see  [here](../examples/hybrid_chunking.ipynb).

## Hierarchical Chunker

The `HierarchicalChunker` implementation uses the document structure information from
the [`DoclingDocument`](./docling_document.md) to create one chunk for each individual
detected document element, by default only merging together list items (can be opted out
via param `merge_list_items`). It also takes care of attaching all relevant document
metadata, including headers and captions.

```
</content>
</file_11>

<file_12>
<path>concepts/docling_document.md</path>
<content>
```markdown
With Docling v2, we introduce a unified document representation format called `DoclingDocument`. It is defined as a
pydantic datatype, which can express several features common to documents, such as:

* Text, Tables, Pictures, and more
* Document hierarchy with sections and groups
* Disambiguation between main body and headers, footers (furniture)
* Layout information (i.e. bounding boxes) for all items, if available
* Provenance information

The definition of the Pydantic types is implemented in the module `docling_core.types.doc`, more details in [source code definitions](https://github.com/DS4SD/docling-core/tree/main/docling_core/types/doc).

It also brings a set of document construction APIs to build up a `DoclingDocument` from scratch.

## Example document structures

To illustrate the features of the `DoclingDocument` format, in the subsections below we consider the
`DoclingDocument` converted from `tests/data/word_sample.docx` and we present some side-by-side comparisons,
where the left side shows snippets from the converted document
serialized as YAML and the right one shows the corresponding parts of the original MS Word.

### Basic structure

A `DoclingDocument` exposes top-level fields for the document content, organized in two categories.
The first category is the _content items_, which are stored in these fields:

- `texts`: All items that have a text representation (paragraph, section heading, equation, ...). Base class is `TextItem`.
- `tables`: All tables, type `TableItem`. Can carry structure annotations.
- `pictures`: All pictures, type `PictureItem`. Can carry structure annotations.
- `key_value_items`: All key-value items.

All of the above fields are lists and store items inheriting from the `DocItem` type. They can express different
data structures depending on their type, and reference parents and children through JSON pointers.

The second category is _content structure_, which is encapsualted in:

- `body`: The root node of a tree-structure for the main document body
- `furniture`: The root node of a tree-structure for all items that don't belong into the body (headers, footers, ...)
- `groups`: A set of items that don't represent content, but act as containers for other content items (e.g. a list, a chapter)

All of the above fields are only storing `NodeItem` instances, which reference children and parents
through JSON pointers.

The reading order of the document is encapsulated through the `body` tree and the order of _children_ in each item
in the tree.

Below example shows how all items in the first page are nested below the `title` item (`#/texts/1`).

![doc_hierarchy_1](../assets/docling_doc_hierarchy_1.png)

### Grouping

Below example shows how all items under the heading "Let's swim" (`#/texts/5`) are nested as chilrden. The children of
"Let's swim" are both text items and groups, which contain the list elements. The group items are stored in the
top-level `groups` field.

![doc_hierarchy_2](../assets/docling_doc_hierarchy_2.png)

<!--
### Tables

TBD

### Pictures

TBD

### Provenance

TBD
 -->

```
</content>
</file_12>

<file_13>
<path>concepts/index.md</path>
<content>
```markdown
Use the navigation on the left to browse through some core Docling concepts.

```
</content>
</file_13>

<file_14>
<path>examples/backend_xml_rag.ipynb</path>
<content>
```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<a href=\"https://colab.research.google.com/github/DS4SD/docling/blob/main/docs/examples/backend_xml_rag.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Conversion of custom XML"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "| Step | Tech | Execution | \n",
    "| --- | --- | --- |\n",
    "| Embedding | Hugging Face / Sentence Transformers | 💻 Local |\n",
    "| Vector store | Milvus | 💻 Local |\n",
    "| Gen AI | Hugging Face Inference API | 🌐 Remote | "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Overview"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This is an example of using [Docling](https://ds4sd.github.io/docling/) for converting structured data (XML) into a unified document\n",
    "representation format, `DoclingDocument`, and leverage its riched structured content for RAG applications.\n",
    "\n",
    "Data used in this example consist of patents from the [United States Patent and Trademark Office (USPTO)](https://www.uspto.gov/) and medical\n",
    "articles from [PubMed Central® (PMC)](https://pmc.ncbi.nlm.nih.gov/).\n",
    "\n",
    "In this notebook, we accomplish the following:\n",
    "- [Simple conversion](#simple-conversion) of supported XML files in a nutshell\n",
    "- An [end-to-end application](#end-to-end-application) using public collections of XML files supported by Docling\n",
    "  - [Setup](#setup) the API access for generative AI\n",
    "  - [Fetch the data](#fetch-the-data) from USPTO and PubMed Central® sites, using Docling custom backends\n",
    "  - [Parse, chunk, and index](#parse-chunk-and-index) the documents in a vector database\n",
    "  - [Perform RAG](#question-answering-with-rag) using [LlamaIndex Docling extension](../../integrations/llamaindex/)\n",
    "\n",
    "For more details on document chunking with Docling, refer to the [Chunking](../../concepts/chunking/) documentation. For RAG with Docling and LlamaIndex, also check the example [RAG with LlamaIndex](../rag_llamaindex/)."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Simple conversion\n",
    "\n",
    "The XML file format defines and stores data in a format that is both human-readable and machine-readable.\n",
    "Because of this flexibility, Docling requires custom backend processors to interpret XML definitions and convert them into `DoclingDocument` objects.\n",
    "\n",
    "Some public data collections in XML format are already supported by Docling (USTPO patents and PMC articles). In these cases, the document conversion is straightforward and the same as with any other supported format, such as PDF or HTML. The execution example in [Simple Conversion](../minimal/) is the recommended usage of Docling for a single file:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "ConversionStatus.SUCCESS\n"
     ]
    }
   ],
   "source": [
    "from docling.document_converter import DocumentConverter\n",
    "\n",
    "# a sample PMC article:\n",
    "source = \"../../tests/data/pubmed/elife-56337.nxml\"\n",
    "converter = DocumentConverter()\n",
    "result = converter.convert(source)\n",
    "print(result.status)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Once the document is converted, it can be exported to any format supported by Docling. For instance, to markdown (showing here the first lines only):"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "# KRAB-zinc finger protein gene expansion in response to active retrotransposons in the murine lineage\n",
      "\n",
      "Wolf Gernot; 1: The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health: Bethesda: United States; de Iaco Alberto; 2: School of Life Sciences, École Polytechnique Fédérale de Lausanne (EPFL): Lausanne: Switzerland; Sun Ming-An; 1: The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health: Bethesda: United States; Bruno Melania; 1: The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health: Bethesda: United States; Tinkham Matthew; 1: The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health: Bethesda: United States; Hoang Don; 1: The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health: Bethesda: United States; Mitra Apratim; 1: The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health: Bethesda: United States; Ralls Sherry; 1: The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health: Bethesda: United States; Trono Didier; 2: School of Life Sciences, École Polytechnique Fédérale de Lausanne (EPFL): Lausanne: Switzerland; Macfarlan Todd S; 1: The Eunice Kennedy Shriver National Institute of Child Health and Human Development, The National Institutes of Health: Bethesda: United States\n",
      "\n",
      "## Abstract\n",
      "\n",
      "The Krüppel-associated box zinc finger protein (KRAB-ZFP) family diversified in mammals. The majority of human KRAB-ZFPs bind transposable elements (TEs), however, since most TEs are inactive in humans it is unclear whether KRAB-ZFPs emerged to suppress TEs. We demonstrate that many recently emerged murine KRAB-ZFPs also bind to TEs, including the active ETn, IAP, and L1 families. Using a CRISPR/Cas9-based engineering approach, we genetically deleted five large clusters of KRAB-ZFPs and demonstrate that target TEs are de-repressed, unleashing TE-encoded enhancers. Homozygous knockout mice lacking one of two KRAB-ZFP gene clusters on chromosome 2 and chromosome 4 were nonetheless viable. In pedigrees of chromosome 4 cluster KRAB-ZFP mutants, we identified numerous novel ETn insertions with a modest increase in mutants. Our data strongly support the current model that recent waves of retrotransposon activity drove the expansion of KRAB-ZFP genes in mice and that many KRAB-ZFPs play a redundant role restricting TE activity.\n",
      "\n"
     ]
    }
   ],
   "source": [
    "md_doc = result.document.export_to_markdown()\n",
    "\n",
    "delim = \"\\n\"\n",
    "print(delim.join(md_doc.split(delim)[:8]))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "If the XML file is not supported, a `ConversionError` message will be raised."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Input document docling_test.xml does not match any allowed format.\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "File format not allowed: docling_test.xml\n"
     ]
    }
   ],
   "source": [
    "from io import BytesIO\n",
    "\n",
    "from docling.datamodel.base_models import DocumentStream\n",
    "from docling.exceptions import ConversionError\n",
    "\n",
    "xml_content = (\n",
    "    b'<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE docling_test SYSTEM '\n",
    "    b'\"test.dtd\"><docling>Random content</docling>'\n",
    ")\n",
    "stream = DocumentStream(name=\"docling_test.xml\", stream=BytesIO(xml_content))\n",
    "try:\n",
    "    result = converter.convert(stream)\n",
    "except ConversionError as ce:\n",
    "    print(ce)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "You can always refer to the [Usage](../../usage/#supported-formats) documentation page for a list of supported formats."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## End-to-end application\n",
    "\n",
    "This section describes a step-by-step application for processing XML files from supported public collections and use them for question-answering."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Setup"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Requirements can be installed as shown below. The `--no-warn-conflicts` argument is meant for Colab's pre-populated Python environment, feel free to remove for stricter usage."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    }
   ],
   "source": [
    "%pip install -q --progress-bar off --no-warn-conflicts llama-index-core llama-index-readers-docling llama-index-node-parser-docling llama-index-embeddings-huggingface llama-index-llms-huggingface-api llama-index-vector-stores-milvus llama-index-readers-file python-dotenv"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This notebook uses HuggingFace's Inference API. For an increased LLM quota, a token can be provided via the environment variable `HF_TOKEN`.\n",
    "\n",
    "If you're running this notebook in Google Colab, make sure you [add](https://medium.com/@parthdasawant/how-to-use-secrets-in-google-colab-450c38e3ec75) your API key as a secret."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from warnings import filterwarnings\n",
    "\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "\n",
    "def _get_env_from_colab_or_os(key):\n",
    "    try:\n",
    "        from google.colab import userdata\n",
    "\n",
    "        try:\n",
    "            return userdata.get(key)\n",
    "        except userdata.SecretNotFoundError:\n",
    "            pass\n",
    "    except ImportError:\n",
    "        pass\n",
    "    return os.getenv(key)\n",
    "\n",
    "\n",
    "load_dotenv()\n",
    "\n",
    "filterwarnings(action=\"ignore\", category=UserWarning, module=\"pydantic\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can now define the main parameters:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pathlib import Path\n",
    "from tempfile import mkdtemp\n",
    "\n",
    "from llama_index.embeddings.huggingface import HuggingFaceEmbedding\n",
    "from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI\n",
    "\n",
    "EMBED_MODEL_ID = \"BAAI/bge-small-en-v1.5\"\n",
    "EMBED_MODEL = HuggingFaceEmbedding(model_name=EMBED_MODEL_ID)\n",
    "TEMP_DIR = Path(mkdtemp())\n",
    "MILVUS_URI = str(TEMP_DIR / \"docling.db\")\n",
    "GEN_MODEL = HuggingFaceInferenceAPI(\n",
    "    token=_get_env_from_colab_or_os(\"HF_TOKEN\"),\n",
    "    model_name=\"mistralai/Mixtral-8x7B-Instruct-v0.1\",\n",
    ")\n",
    "embed_dim = len(EMBED_MODEL.get_text_embedding(\"hi\"))\n",
    "# https://github.com/huggingface/transformers/issues/5486:\n",
    "os.environ[\"TOKENIZERS_PARALLELISM\"] = \"false\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Fetch the data"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "In this notebook we will use XML data from collections supported by Docling:\n",
    "- Medical articles from the [PubMed Central® (PMC)](https://pmc.ncbi.nlm.nih.gov/). They are available in an [FTP server](https://ftp.ncbi.nlm.nih.gov/pub/pmc/) as `.tar.gz` files. Each file contains the full article data in XML format, among other supplementary files like images or spreadsheets.\n",
    "- Patents from the [United States Patent and Trademark Office](https://www.uspto.gov/). They are available in the [Bulk Data Storage System (BDSS)](https://bulkdata.uspto.gov/) as zip files. Each zip file may contain several patents in XML format.\n",
    "\n",
    "The raw files will be downloaded form the source and saved in a temporary directory."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "#### PMC articles\n",
    "\n",
    "The [OA file](https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.csv) is a manifest file of all the PMC articles, including the URL path to download the source files. In this notebook we will use as example the article [Pathogens spread by high-altitude windborne mosquitoes](https://pmc.ncbi.nlm.nih.gov/articles/PMC11703268/), which is available in the archive file [PMC11703268.tar.gz](https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/e3/6b/PMC11703268.tar.gz)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Downloading https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/e3/6b/PMC11703268.tar.gz...\n",
      "Extracting and storing the XML file containing the article text...\n",
      "Stored XML file nihpp-2024.12.26.630351v1.nxml\n"
     ]
    }
   ],
   "source": [
    "import tarfile\n",
    "from io import BytesIO\n",
    "\n",
    "import requests\n",
    "\n",
    "# PMC article PMC11703268\n",
    "url: str = \"https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/e3/6b/PMC11703268.tar.gz\"\n",
    "\n",
    "print(f\"Downloading {url}...\")\n",
    "buf = BytesIO(requests.get(url).content)\n",
    "print(\"Extracting and storing the XML file containing the article text...\")\n",
    "with tarfile.open(fileobj=buf, mode=\"r:gz\") as tar_file:\n",
    "    for tarinfo in tar_file:\n",
    "        if tarinfo.isreg():\n",
    "            file_path = Path(tarinfo.name)\n",
    "            if file_path.suffix == \".nxml\":\n",
    "                with open(TEMP_DIR / file_path.name, \"wb\") as file_obj:\n",
    "                    file_obj.write(tar_file.extractfile(tarinfo).read())\n",
    "                print(f\"Stored XML file {file_path.name}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "#### USPTO patents\n",
    "\n",
    "Since each USPTO file is a concatenation of several patents, we need to split its content into valid XML pieces. The following code downloads a sample zip file, split its content in sections, and dumps each section as an XML file. For simplicity, this pipeline is shown here in a sequential manner, but it could be parallelized."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import zipfile\n",
    "\n",
    "# Patent grants from December 17-23, 2024\n",
    "url: str = (\n",
    "    \"https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2024/ipg241217.zip\"\n",
    ")\n",
    "XML_SPLITTER: str = '<?xml version=\"1.0\"'\n",
    "doc_num: int = 0\n",
    "\n",
    "print(f\"Downloading {url}...\")\n",
    "buf = BytesIO(requests.get(url).content)\n",
    "print(f\"Parsing zip file, splitting into XML sections, and exporting to files...\")\n",
    "with zipfile.ZipFile(buf) as zf:\n",
    "    res = zf.testzip()\n",
    "    if res:\n",
    "        print(\"Error validating zip file\")\n",
    "    else:\n",
    "        with zf.open(zf.namelist()[0]) as xf:\n",
    "            is_patent = False\n",
    "            patent_buffer = BytesIO()\n",
    "            for xf_line in xf:\n",
    "                decoded_line = xf_line.decode(errors=\"ignore\").rstrip()\n",
    "                xml_index = decoded_line.find(XML_SPLITTER)\n",
    "                if xml_index != -1:\n",
    "                    if (\n",
    "                        xml_index > 0\n",
    "                    ):  # cases like </sequence-cwu><?xml version=\"1.0\"...\n",
    "                        patent_buffer.write(xf_line[:xml_index])\n",
    "                        patent_buffer.write(b\"\\r\\n\")\n",
    "                        xf_line = xf_line[xml_index:]\n",
    "                    if patent_buffer.getbuffer().nbytes > 0 and is_patent:\n",
    "                        doc_num += 1\n",
    "                        patent_id = f\"ipg241217-{doc_num}\"\n",
    "                        with open(TEMP_DIR / f\"{patent_id}.xml\", \"wb\") as file_obj:\n",
    "                            file_obj.write(patent_buffer.getbuffer())\n",
    "                    is_patent = False\n",
    "                    patent_buffer = BytesIO()\n",
    "                elif decoded_line.startswith(\"<!DOCTYPE\"):\n",
    "                    is_patent = True\n",
    "                patent_buffer.write(xf_line)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Fetched and exported 4014 documents.\n"
     ]
    }
   ],
   "source": [
    "print(f\"Fetched and exported {doc_num} documents.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Using the backend converter (optional)\n",
    "\n",
    "- The custom backend converters `PubMedDocumentBackend` and `PatentUsptoDocumentBackend` aim at handling the parsing of PMC articles and USPTO patents, respectively.\n",
    "- As any other backends, you can leverage the function `is_valid()` to check if the input document is supported by the this backend.\n",
    "- Note that some XML sections in the original USPTO zip file may not represent patents, like sequence listings, and therefore they will show as invalid by the backend."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Document nihpp-2024.12.26.630351v1.nxml is a valid PMC article? True\n",
      "Document ipg241217-1.xml is a valid patent? True\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "3964d1ff30f74588a2f6b53ca8865a9f",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "  0%|          | 0/4014 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Found 3928 patents out of 4014 XML files.\n"
     ]
    }
   ],
   "source": [
    "from tqdm.notebook import tqdm\n",
    "\n",
    "from docling.backend.xml.pubmed_backend import PubMedDocumentBackend\n",
    "from docling.backend.xml.uspto_backend import PatentUsptoDocumentBackend\n",
    "from docling.datamodel.base_models import InputFormat\n",
    "from docling.datamodel.document import InputDocument\n",
    "\n",
    "# check PMC\n",
    "in_doc = InputDocument(\n",
    "    path_or_stream=TEMP_DIR / \"nihpp-2024.12.26.630351v1.nxml\",\n",
    "    format=InputFormat.XML_PUBMED,\n",
    "    backend=PubMedDocumentBackend,\n",
    ")\n",
    "backend = PubMedDocumentBackend(\n",
    "    in_doc=in_doc, path_or_stream=TEMP_DIR / \"nihpp-2024.12.26.630351v1.nxml\"\n",
    ")\n",
    "print(f\"Document {in_doc.file.name} is a valid PMC article? {backend.is_valid()}\")\n",
    "\n",
    "# check USPTO\n",
    "in_doc = InputDocument(\n",
    "    path_or_stream=TEMP_DIR / \"ipg241217-1.xml\",\n",
    "    format=InputFormat.XML_USPTO,\n",
    "    backend=PatentUsptoDocumentBackend,\n",
    ")\n",
    "backend = PatentUsptoDocumentBackend(\n",
    "    in_doc=in_doc, path_or_stream=TEMP_DIR / \"ipg241217-1.xml\"\n",
    ")\n",
    "print(f\"Document {in_doc.file.name} is a valid patent? {backend.is_valid()}\")\n",
    "\n",
    "patent_valid = 0\n",
    "pbar = tqdm(TEMP_DIR.glob(\"*.xml\"), total=doc_num)\n",
    "for in_path in pbar:\n",
    "    in_doc = InputDocument(\n",
    "        path_or_stream=in_path,\n",
    "        format=InputFormat.XML_USPTO,\n",
    "        backend=PatentUsptoDocumentBackend,\n",
    "    )\n",
    "    backend = PatentUsptoDocumentBackend(in_doc=in_doc, path_or_stream=in_path)\n",
    "    patent_valid += int(backend.is_valid())\n",
    "\n",
    "print(f\"Found {patent_valid} patents out of {doc_num} XML files.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Calling the function `convert()` will convert the input document into a `DoclingDocument`"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Patent \"Semiconductor package\" has 19 claims\n"
     ]
    }
   ],
   "source": [
    "doc = backend.convert()\n",
    "\n",
    "claims_sec = [item for item in doc.texts if item.text == \"CLAIMS\"][0]\n",
    "print(f'Patent \"{doc.texts[0].text}\" has {len(claims_sec.children)} claims')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "✏️ **Tip**: in general, there is no need to use the backend converters to parse USPTO or PubMed XML files. The generic `DocumentConverter` object tries to guess the input document format and applies the corresponding backend parser. The conversion shown in [Simple Conversion](#simple-conversion) is the recommended usage for the supported XML files."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Parse, chunk, and index"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The `DoclingDocument` format of the converted patents has a rich hierarchical structure, inherited from the original XML document and preserved by the Docling custom backend.\n",
    "In this notebook, we will leverage:\n",
    "- The `SimpleDirectoryReader` pattern to iterate over the exported XML files created in section [Fetch the data](#fetch-the-data).\n",
    "- The LlamaIndex extensions, `DoclingReader` and `DoclingNodeParser`, to ingest the patent chunks into a Milvus vectore store.\n",
    "- The `HierarchicalChunker` implementation, which applies a document-based hierarchical chunking, to leverage the patent structures like sections and paragraphs within sections.\n",
    "\n",
    "Refer to other possible implementations and usage patterns in the [Chunking](../../concepts/chunking/) documentation and the [RAG with LlamaIndex](../rag_llamaindex/) notebook."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "##### Set the Docling reader and the directory reader\n",
    "\n",
    "Note that `DoclingReader` uses Docling's `DocumentConverter` by default and therefore it will recognize the format of the XML files and leverage the `PatentUsptoDocumentBackend` automatically.\n",
    "\n",
    "For demonstration purposes, we limit the scope of the analysis to the first 100 patents."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "from llama_index.core import SimpleDirectoryReader\n",
    "from llama_index.readers.docling import DoclingReader\n",
    "\n",
    "reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)\n",
    "dir_reader = SimpleDirectoryReader(\n",
    "    input_dir=TEMP_DIR,\n",
    "    exclude=[\"docling.db\", \"*.nxml\"],\n",
    "    file_extractor={\".xml\": reader},\n",
    "    filename_as_id=True,\n",
    "    num_files_limit=100,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "##### Set the node parser\n",
    "\n",
    "Note that the `HierarchicalChunker` is the default chunking implementation of the `DoclingNodeParser`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "from llama_index.node_parser.docling import DoclingNodeParser\n",
    "\n",
    "node_parser = DoclingNodeParser()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "##### Set a local Milvus database and run the ingestion"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2025-01-24 16:49:57,108 [DEBUG][_create_connection]: Created new connection using: 2d58fad6c63448a486c0c0ffe3b7b28c (async_milvus_client.py:600)\n",
      "Loading files:  51%|█████     | 51/100 [00:00<00:00, 67.88file/s]Input document ipg241217-1050.xml does not match any allowed format.\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Failed to load file /var/folders/2r/b2sdj1512g1_0m7wzzy7sftr0000gn/T/tmp11rjcdj8/ipg241217-1050.xml with error: File format not allowed: /var/folders/2r/b2sdj1512g1_0m7wzzy7sftr0000gn/T/tmp11rjcdj8/ipg241217-1050.xml. Skipping...\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Loading files: 100%|██████████| 100/100 [00:01<00:00, 58.05file/s]\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "e9208639f1a4418d97267a28305d18fa",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Parsing nodes:   0%|          | 0/99 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "88026613f6f44f0c8476dceaa1cb78cd",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Generating embeddings:   0%|          | 0/2048 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "7522b8b434b54616b4cfc3d71e9556d7",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Generating embeddings:   0%|          | 0/2048 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "5879d8161c2041f5b100959e69ff9017",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Generating embeddings:   0%|          | 0/2048 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "557912b5e3c741f3a06127156bc46379",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Generating embeddings:   0%|          | 0/2048 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "843bb145942b449aa55fc5b8208da734",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Generating embeddings:   0%|          | 0/2048 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "c7dba09a4aed422998e9b9c2c3a70317",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Generating embeddings:   0%|          | 0/2048 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "0bd031356c7e4e879dcbe1d04e6c4a4e",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Generating embeddings:   0%|          | 0/425 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from llama_index.core import StorageContext, VectorStoreIndex\n",
    "from llama_index.vector_stores.milvus import MilvusVectorStore\n",
    "\n",
    "vector_store = MilvusVectorStore(\n",
    "    uri=MILVUS_URI,\n",
    "    dim=embed_dim,\n",
    "    overwrite=True,\n",
    ")\n",
    "\n",
    "index = VectorStoreIndex.from_documents(\n",
    "    documents=dir_reader.load_data(show_progress=True),\n",
    "    transformations=[node_parser],\n",
    "    storage_context=StorageContext.from_defaults(vector_store=vector_store),\n",
    "    embed_model=EMBED_MODEL,\n",
    "    show_progress=True,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Finally, add the PMC article to the vector store directly from the reader."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "<llama_index.core.indices.vector_store.base.VectorStoreIndex at 0x373a7f7d0>"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "index.from_documents(\n",
    "    documents=reader.load_data(TEMP_DIR / \"nihpp-2024.12.26.630351v1.nxml\"),\n",
    "    transformations=[node_parser],\n",
    "    storage_context=StorageContext.from_defaults(vector_store=vector_store),\n",
    "    embed_model=EMBED_MODEL,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Question-answering with RAG"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The retriever can be used to identify highly relevant documents:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Node ID: 5afd36c0-a739-4a88-a51c-6d0f75358db5\n",
      "Text: The portable fitness monitoring device 102 may be a device such\n",
      "as, for example, a mobile phone, a personal digital assistant, a music\n",
      "file player (e.g. and MP3 player), an intelligent article for wearing\n",
      "(e.g. a fitness monitoring garment, wrist band, or watch), a dongle\n",
      "(e.g. a small hardware device that protects software) that includes a\n",
      "fitn...\n",
      "Score:  0.772\n",
      "\n",
      "Node ID: f294b5fd-9089-43cb-8c4e-d1095a634ff1\n",
      "Text: US Patent Application US 20120071306 entitled “Portable\n",
      "Multipurpose Whole Body Exercise Device” discloses a portable\n",
      "multipurpose whole body exercise device which can be used for general\n",
      "fitness, Pilates-type, core strengthening, therapeutic, and\n",
      "rehabilitative exercises as well as stretching and physical therapy\n",
      "and which includes storable acc...\n",
      "Score:  0.749\n",
      "\n",
      "Node ID: 8251c7ef-1165-42e1-8c91-c99c8a711bf7\n",
      "Text: Program products, methods, and systems for providing fitness\n",
      "monitoring services of the present invention can include any software\n",
      "application executed by one or more computing devices. A computing\n",
      "device can be any type of computing device having one or more\n",
      "processors. For example, a computing device can be a workstation,\n",
      "mobile device (e.g., ...\n",
      "Score:  0.744\n",
      "\n"
     ]
    }
   ],
   "source": [
    "retriever = index.as_retriever(similarity_top_k=3)\n",
    "results = retriever.retrieve(\"What patents are related to fitness devices?\")\n",
    "\n",
    "for item in results:\n",
    "    print(item)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "With the query engine, we can run the question-answering with the RAG pattern on the set of indexed documents.\n",
    "\n",
    "First, we can prompt the LLM directly:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">╭──────────────────────────────────────────────────── Prompt ─────────────────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│</span> Do mosquitoes in high altitude expand viruses over large distances?                                             <span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;31m╭─\u001b[0m\u001b[1;31m───────────────────────────────────────────────────\u001b[0m\u001b[1;31m Prompt \u001b[0m\u001b[1;31m────────────────────────────────────────────────────\u001b[0m\u001b[1;31m─╮\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m Do mosquitoes in high altitude expand viruses over large distances?                                             \u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╭─────────────────────────────────────────────── Generated Content ───────────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> Mosquitoes can be found at high altitudes, but their ability to transmit viruses over long distances is not     <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> primarily dependent on altitude. Mosquitoes are vectors for various diseases, such as malaria, dengue fever,    <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> and Zika virus, and their transmission range is more closely related to their movement, the presence of a host, <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> and environmental conditions that support their survival and reproduction.                                      <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>                                                                                                                 <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> At high altitudes, the environment can be less suitable for mosquitoes due to factors such as colder            <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> temperatures, lower humidity, and stronger winds, which can limit their population size and distribution.       <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> However, some species of mosquitoes have adapted to high-altitude environments and can still transmit diseases  <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> in these areas.                                                                                                 <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>                                                                                                                 <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> It is possible for mosquitoes to be transported by wind or human activities to higher altitudes, but this is    <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> not a significant factor in their ability to transmit viruses over long distances. Instead, long-distance       <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> transmission of viruses is more often associated with human travel and transportation, which can rapidly spread <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> infected mosquitoes or humans to new areas, leading to the spread of disease.                                   <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;32m╭─\u001b[0m\u001b[1;32m──────────────────────────────────────────────\u001b[0m\u001b[1;32m Generated Content \u001b[0m\u001b[1;32m──────────────────────────────────────────────\u001b[0m\u001b[1;32m─╮\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m Mosquitoes can be found at high altitudes, but their ability to transmit viruses over long distances is not     \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m primarily dependent on altitude. Mosquitoes are vectors for various diseases, such as malaria, dengue fever,    \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m and Zika virus, and their transmission range is more closely related to their movement, the presence of a host, \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m and environmental conditions that support their survival and reproduction.                                      \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m                                                                                                                 \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m At high altitudes, the environment can be less suitable for mosquitoes due to factors such as colder            \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m temperatures, lower humidity, and stronger winds, which can limit their population size and distribution.       \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m However, some species of mosquitoes have adapted to high-altitude environments and can still transmit diseases  \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m in these areas.                                                                                                 \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m                                                                                                                 \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m It is possible for mosquitoes to be transported by wind or human activities to higher altitudes, but this is    \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m not a significant factor in their ability to transmit viruses over long distances. Instead, long-distance       \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m transmission of viruses is more often associated with human travel and transportation, which can rapidly spread \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m infected mosquitoes or humans to new areas, leading to the spread of disease.                                   \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from llama_index.core.base.llms.types import ChatMessage, MessageRole\n",
    "from rich.console import Console\n",
    "from rich.panel import Panel\n",
    "\n",
    "console = Console()\n",
    "query = \"Do mosquitoes in high altitude expand viruses over large distances?\"\n",
    "\n",
    "usr_msg = ChatMessage(role=MessageRole.USER, content=query)\n",
    "response = GEN_MODEL.chat(messages=[usr_msg])\n",
    "\n",
    "console.print(Panel(query, title=\"Prompt\", border_style=\"bold red\"))\n",
    "console.print(\n",
    "    Panel(\n",
    "        response.message.content.strip(),\n",
    "        title=\"Generated Content\",\n",
    "        border_style=\"bold green\",\n",
    "    )\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Now, we can compare the response when the model is prompted with the indexed PMC article as supporting context:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╭────────────────────────────────────────── Generated Content with RAG ───────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> Yes, mosquitoes in high altitude can expand viruses over large distances. A study intercepted 1,017 female      <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> mosquitoes at altitudes of 120-290 m above ground over Mali and Ghana and screened them for infection with      <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> arboviruses, plasmodia, and filariae. The study found that 3.5% of the mosquitoes were infected with            <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> flaviviruses, and 1.1% were infectious. Additionally, the study identified 19 mosquito-borne pathogens,         <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> including three arboviruses that affect humans (dengue, West Nile, and M’Poko viruses). The study provides      <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> compelling evidence that mosquito-borne pathogens are often spread by windborne mosquitoes at altitude.         <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;32m╭─\u001b[0m\u001b[1;32m─────────────────────────────────────────\u001b[0m\u001b[1;32m Generated Content with RAG \u001b[0m\u001b[1;32m──────────────────────────────────────────\u001b[0m\u001b[1;32m─╮\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m Yes, mosquitoes in high altitude can expand viruses over large distances. A study intercepted 1,017 female      \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m mosquitoes at altitudes of 120-290 m above ground over Mali and Ghana and screened them for infection with      \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m arboviruses, plasmodia, and filariae. The study found that 3.5% of the mosquitoes were infected with            \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m flaviviruses, and 1.1% were infectious. Additionally, the study identified 19 mosquito-borne pathogens,         \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m including three arboviruses that affect humans (dengue, West Nile, and M’Poko viruses). The study provides      \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m compelling evidence that mosquito-borne pathogens are often spread by windborne mosquitoes at altitude.         \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters\n",
    "\n",
    "filters = MetadataFilters(\n",
    "    filters=[\n",
    "        ExactMatchFilter(key=\"filename\", value=\"nihpp-2024.12.26.630351v1.nxml\"),\n",
    "    ]\n",
    ")\n",
    "\n",
    "query_engine = index.as_query_engine(llm=GEN_MODEL, filter=filters, similarity_top_k=3)\n",
    "result = query_engine.query(query)\n",
    "\n",
    "console.print(\n",
    "    Panel(\n",
    "        result.response.strip(),\n",
    "        title=\"Generated Content with RAG\",\n",
    "        border_style=\"bold green\",\n",
    "    )\n",
    ")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

```
</content>
</file_14>

<file_15>
<path>examples/batch_convert.py</path>
<content>
```python
import json
import logging
import time
from pathlib import Path
from typing import Iterable

import yaml

from docling.datamodel.base_models import ConversionStatus
from docling.datamodel.document import ConversionResult
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter

_log = logging.getLogger(__name__)

USE_V2 = True
USE_LEGACY = True


def export_documents(
    conv_results: Iterable[ConversionResult],
    output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failure_count = 0
    partial_success_count = 0

    for conv_res in conv_results:
        if conv_res.status == ConversionStatus.SUCCESS:
            success_count += 1
            doc_filename = conv_res.input.file.stem

            if USE_V2:
                # Export Docling document format to JSON:
                with (output_dir / f"{doc_filename}.json").open("w") as fp:
                    fp.write(json.dumps(conv_res.document.export_to_dict()))

                # Export Docling document format to YAML:
                with (output_dir / f"{doc_filename}.yaml").open("w") as fp:
                    fp.write(yaml.safe_dump(conv_res.document.export_to_dict()))

                # Export Docling document format to doctags:
                with (output_dir / f"{doc_filename}.doctags.txt").open("w") as fp:
                    fp.write(conv_res.document.export_to_document_tokens())

                # Export Docling document format to markdown:
                with (output_dir / f"{doc_filename}.md").open("w") as fp:
                    fp.write(conv_res.document.export_to_markdown())

                # Export Docling document format to text:
                with (output_dir / f"{doc_filename}.txt").open("w") as fp:
                    fp.write(conv_res.document.export_to_markdown(strict_text=True))

            if USE_LEGACY:
                # Export Deep Search document JSON format:
                with (output_dir / f"{doc_filename}.legacy.json").open(
                    "w", encoding="utf-8"
                ) as fp:
                    fp.write(json.dumps(conv_res.legacy_document.export_to_dict()))

                # Export Text format:
                with (output_dir / f"{doc_filename}.legacy.txt").open(
                    "w", encoding="utf-8"
                ) as fp:
                    fp.write(
                        conv_res.legacy_document.export_to_markdown(strict_text=True)
                    )

                # Export Markdown format:
                with (output_dir / f"{doc_filename}.legacy.md").open(
                    "w", encoding="utf-8"
                ) as fp:
                    fp.write(conv_res.legacy_document.export_to_markdown())

                # Export Document Tags format:
                with (output_dir / f"{doc_filename}.legacy.doctags.txt").open(
                    "w", encoding="utf-8"
                ) as fp:
                    fp.write(conv_res.legacy_document.export_to_document_tokens())

        elif conv_res.status == ConversionStatus.PARTIAL_SUCCESS:
            _log.info(
                f"Document {conv_res.input.file} was partially converted with the following errors:"
            )
            for item in conv_res.errors:
                _log.info(f"\t{item.error_message}")
            partial_success_count += 1
        else:
            _log.info(f"Document {conv_res.input.file} failed to convert.")
            failure_count += 1

    _log.info(
        f"Processed {success_count + partial_success_count + failure_count} docs, "
        f"of which {failure_count} failed "
        f"and {partial_success_count} were partially converted."
    )
    return success_count, partial_success_count, failure_count


def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_paths = [
        Path("./tests/data/2206.01062.pdf"),
        Path("./tests/data/2203.01017v2.pdf"),
        Path("./tests/data/2305.03393v1.pdf"),
        Path("./tests/data/redp5110_sampled.pdf"),
    ]

    # buf = BytesIO(Path("./test/data/2206.01062.pdf").open("rb").read())
    # docs = [DocumentStream(name="my_doc.pdf", stream=buf)]
    # input = DocumentConversionInput.from_streams(docs)

    # # Turn on inline debug visualizations:
    # settings.debug.visualize_layout = True
    # settings.debug.visualize_ocr = True
    # settings.debug.visualize_tables = True
    # settings.debug.visualize_cells = True

    doc_converter = DocumentConverter()

    start_time = time.time()

    conv_results = doc_converter.convert_all(
        input_doc_paths,
        raises_on_error=False,  # to let conversion run through all and examine results at the end
    )
    success_count, partial_success_count, failure_count = export_documents(
        conv_results, output_dir=Path("scratch")
    )

    end_time = time.time() - start_time

    _log.info(f"Document conversion complete in {end_time:.2f} seconds.")

    if failure_count > 0:
        raise RuntimeError(
            f"The example failed converting {failure_count} on {len(input_doc_paths)}."
        )


if __name__ == "__main__":
    main()

```
</content>
</file_15>

<file_16>
<path>examples/custom_convert.py</path>
<content>
```python
import json
import logging
import time
from pathlib import Path

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.ocr_mac_model import OcrMacOptions
from docling.models.tesseract_ocr_cli_model import TesseractCliOcrOptions
from docling.models.tesseract_ocr_model import TesseractOcrOptions

_log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/2206.01062.pdf")

    ###########################################################################

    # The following sections contain a combination of PipelineOptions
    # and PDF Backends for various configurations.
    # Uncomment one section at the time to see the differences in the output.

    # PyPdfium without EasyOCR
    # --------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = False
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = False

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(
    #             pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend
    #         )
    #     }
    # )

    # PyPdfium with EasyOCR
    # -----------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(
    #             pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend
    #         )
    #     }
    # )

    # Docling Parse without EasyOCR
    # -------------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = False
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    # Docling Parse with EasyOCR
    # ----------------------
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.ocr_options.lang = ["es"]
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.AUTO
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # Docling Parse with EasyOCR (CPU only)
    # ----------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.ocr_options.use_gpu = False  # <-- set this.
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    # Docling Parse with Tesseract
    # ----------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True
    # pipeline_options.ocr_options = TesseractOcrOptions()

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    # Docling Parse with Tesseract CLI
    # ----------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True
    # pipeline_options.ocr_options = TesseractCliOcrOptions()

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    # Docling Parse with ocrmac(Mac only)
    # ----------------------
    # pipeline_options = PdfPipelineOptions()
    # pipeline_options.do_ocr = True
    # pipeline_options.do_table_structure = True
    # pipeline_options.table_structure_options.do_cell_matching = True
    # pipeline_options.ocr_options = OcrMacOptions()

    # doc_converter = DocumentConverter(
    #     format_options={
    #         InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    #     }
    # )

    ###########################################################################

    start_time = time.time()
    conv_result = doc_converter.convert(input_doc_path)
    end_time = time.time() - start_time

    _log.info(f"Document converted in {end_time:.2f} seconds.")

    ## Export results
    output_dir = Path("scratch")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_result.input.file.stem

    # Export Deep Search document JSON format:
    with (output_dir / f"{doc_filename}.json").open("w", encoding="utf-8") as fp:
        fp.write(json.dumps(conv_result.document.export_to_dict()))

    # Export Text format:
    with (output_dir / f"{doc_filename}.txt").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_text())

    # Export Markdown format:
    with (output_dir / f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_markdown())

    # Export Document Tags format:
    with (output_dir / f"{doc_filename}.doctags").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_document_tokens())


if __name__ == "__main__":
    main()

```
</content>
</file_16>

<file_17>
<path>examples/develop_formula_understanding.py</path>
<content>
```python
import logging
from pathlib import Path
from typing import Iterable

from docling_core.types.doc import DocItemLabel, DoclingDocument, NodeItem, TextItem

from docling.datamodel.base_models import InputFormat, ItemAndImageEnrichmentElement
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.base_model import BaseItemAndImageEnrichmentModel
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline


class ExampleFormulaUnderstandingPipelineOptions(PdfPipelineOptions):
    do_formula_understanding: bool = True


# A new enrichment model using both the document element and its image as input
class ExampleFormulaUnderstandingEnrichmentModel(BaseItemAndImageEnrichmentModel):
    images_scale = 2.6

    def __init__(self, enabled: bool):
        self.enabled = enabled

    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        return (
            self.enabled
            and isinstance(element, TextItem)
            and element.label == DocItemLabel.FORMULA
        )

    def __call__(
        self,
        doc: DoclingDocument,
        element_batch: Iterable[ItemAndImageEnrichmentElement],
    ) -> Iterable[NodeItem]:
        if not self.enabled:
            return

        for enrich_element in element_batch:
            enrich_element.image.show()

            yield enrich_element.item


# How the pipeline can be extended.
class ExampleFormulaUnderstandingPipeline(StandardPdfPipeline):

    def __init__(self, pipeline_options: ExampleFormulaUnderstandingPipelineOptions):
        super().__init__(pipeline_options)
        self.pipeline_options: ExampleFormulaUnderstandingPipelineOptions

        self.enrichment_pipe = [
            ExampleFormulaUnderstandingEnrichmentModel(
                enabled=self.pipeline_options.do_formula_understanding
            )
        ]

        if self.pipeline_options.do_formula_understanding:
            self.keep_backend = True

    @classmethod
    def get_default_options(cls) -> ExampleFormulaUnderstandingPipelineOptions:
        return ExampleFormulaUnderstandingPipelineOptions()


# Example main. In the final version, we simply have to set do_formula_understanding to true.
def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/2203.01017v2.pdf")

    pipeline_options = ExampleFormulaUnderstandingPipelineOptions()
    pipeline_options.do_formula_understanding = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ExampleFormulaUnderstandingPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )
    result = doc_converter.convert(input_doc_path)


if __name__ == "__main__":
    main()

```
</content>
</file_17>

<file_18>
<path>examples/develop_picture_enrichment.py</path>
<content>
```python
import logging
from pathlib import Path
from typing import Any, Iterable

from docling_core.types.doc import (
    DoclingDocument,
    NodeItem,
    PictureClassificationClass,
    PictureClassificationData,
    PictureItem,
)

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.base_model import BaseEnrichmentModel
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline


class ExamplePictureClassifierPipelineOptions(PdfPipelineOptions):
    do_picture_classifer: bool = True


class ExamplePictureClassifierEnrichmentModel(BaseEnrichmentModel):
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        return self.enabled and isinstance(element, PictureItem)

    def __call__(
        self, doc: DoclingDocument, element_batch: Iterable[NodeItem]
    ) -> Iterable[Any]:
        if not self.enabled:
            return

        for element in element_batch:
            assert isinstance(element, PictureItem)

            # uncomment this to interactively visualize the image
            # element.get_image(doc).show()

            element.annotations.append(
                PictureClassificationData(
                    provenance="example_classifier-0.0.1",
                    predicted_classes=[
                        PictureClassificationClass(class_name="dummy", confidence=0.42)
                    ],
                )
            )

            yield element


class ExamplePictureClassifierPipeline(StandardPdfPipeline):
    def __init__(self, pipeline_options: ExamplePictureClassifierPipelineOptions):
        super().__init__(pipeline_options)
        self.pipeline_options: ExamplePictureClassifierPipeline

        self.enrichment_pipe = [
            ExamplePictureClassifierEnrichmentModel(
                enabled=pipeline_options.do_picture_classifer
            )
        ]

    @classmethod
    def get_default_options(cls) -> ExamplePictureClassifierPipelineOptions:
        return ExamplePictureClassifierPipelineOptions()


def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/2206.01062.pdf")

    pipeline_options = ExamplePictureClassifierPipelineOptions()
    pipeline_options.images_scale = 2.0
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ExamplePictureClassifierPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )
    result = doc_converter.convert(input_doc_path)

    for element, _level in result.document.iterate_items():
        if isinstance(element, PictureItem):
            print(
                f"The model populated the `data` portion of picture {element.self_ref}:\n{element.annotations}"
            )


if __name__ == "__main__":
    main()

```
</content>
</file_18>

<file_19>
<path>examples/export_figures.py</path>
<content>
```python
import logging
import time
from pathlib import Path

from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0


def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/2206.01062.pdf")
    output_dir = Path("scratch")

    # Important: For operating with page images, we must keep them, otherwise the DocumentConverter
    # will destroy them for cleaning up memory.
    # This is done by setting PdfPipelineOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    # The PdfPipelineOptions.generate_* are the selectors for the document elements which will be enriched
    # with the image field
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_res.input.file.stem

    # Save page images
    for page_no, page in conv_res.document.pages.items():
        page_no = page.page_no
        page_image_filename = output_dir / f"{doc_filename}-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")

    # Save images of figures and tables
    table_counter = 0
    picture_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-table-{table_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

        if isinstance(element, PictureItem):
            picture_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

    # Save markdown with embedded pictures
    md_filename = output_dir / f"{doc_filename}-with-images.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    # Save markdown with externally referenced pictures
    md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

    # Save HTML with externally referenced pictures
    html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
    conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

    end_time = time.time() - start_time

    _log.info(f"Document converted and figures exported in {end_time:.2f} seconds.")


if __name__ == "__main__":
    main()

```
</content>
</file_19>

<file_20>
<path>examples/export_multimodal.py</path>
<content>
```python
import datetime
import logging
import time
from pathlib import Path

import pandas as pd

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.utils.export import generate_multimodal_pages
from docling.utils.utils import create_hash

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0


def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/2206.01062.pdf")
    output_dir = Path("scratch")

    # Important: For operating with page images, we must keep them, otherwise the DocumentConverter
    # will destroy them for cleaning up memory.
    # This is done by setting AssembleOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for (
        content_text,
        content_md,
        content_dt,
        page_cells,
        page_segments,
        page,
    ) in generate_multimodal_pages(conv_res):

        dpi = page._default_image_scale * 72

        rows.append(
            {
                "document": conv_res.input.file.name,
                "hash": conv_res.input.document_hash,
                "page_hash": create_hash(
                    conv_res.input.document_hash + ":" + str(page.page_no - 1)
                ),
                "image": {
                    "width": page.image.width,
                    "height": page.image.height,
                    "bytes": page.image.tobytes(),
                },
                "cells": page_cells,
                "contents": content_text,
                "contents_md": content_md,
                "contents_dt": content_dt,
                "segments": page_segments,
                "extra": {
                    "page_num": page.page_no + 1,
                    "width_in_points": page.size.width,
                    "height_in_points": page.size.height,
                    "dpi": dpi,
                },
            }
        )

    # Generate one parquet from all documents
    df = pd.json_normalize(rows)
    now = datetime.datetime.now()
    output_filename = output_dir / f"multimodal_{now:%Y-%m-%d_%H%M%S}.parquet"
    df.to_parquet(output_filename)

    end_time = time.time() - start_time

    _log.info(
        f"Document converted and multimodal pages generated in {end_time:.2f} seconds."
    )

    # This block demonstrates how the file can be opened with the HF datasets library
    # from datasets import Dataset
    # from PIL import Image
    # multimodal_df = pd.read_parquet(output_filename)

    # # Convert pandas DataFrame to Hugging Face Dataset and load bytes into image
    # dataset = Dataset.from_pandas(multimodal_df)
    # def transforms(examples):
    #     examples["image"] = Image.frombytes('RGB', (examples["image.width"], examples["image.height"]), examples["image.bytes"], 'raw')
    #     return examples
    # dataset = dataset.map(transforms)


if __name__ == "__main__":
    main()

```
</content>
</file_20>

<file_21>
<path>examples/export_tables.py</path>
<content>
```python
import logging
import time
from pathlib import Path

import pandas as pd

from docling.document_converter import DocumentConverter

_log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/2206.01062.pdf")
    output_dir = Path("scratch")

    doc_converter = DocumentConverter()

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    doc_filename = conv_res.input.file.stem

    # Export tables
    for table_ix, table in enumerate(conv_res.document.tables):
        table_df: pd.DataFrame = table.export_to_dataframe()
        print(f"## Table {table_ix}")
        print(table_df.to_markdown())

        # Save the table as csv
        element_csv_filename = output_dir / f"{doc_filename}-table-{table_ix+1}.csv"
        _log.info(f"Saving CSV table to {element_csv_filename}")
        table_df.to_csv(element_csv_filename)

        # Save the table as html
        element_html_filename = output_dir / f"{doc_filename}-table-{table_ix+1}.html"
        _log.info(f"Saving HTML table to {element_html_filename}")
        with element_html_filename.open("w") as fp:
            fp.write(table.export_to_html())

    end_time = time.time() - start_time

    _log.info(f"Document converted and tables exported in {end_time:.2f} seconds.")


if __name__ == "__main__":
    main()

```
</content>
</file_21>

<file_22>
<path>examples/full_page_ocr.py</path>
<content>
```python
from pathlib import Path

from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    OcrMacOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption


def main():
    input_doc = Path("./tests/data/2206.01062.pdf")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    # Any of the OCR options can be used:EasyOcrOptions, TesseractOcrOptions, TesseractCliOcrOptions, OcrMacOptions(Mac only), RapidOcrOptions
    # ocr_options = EasyOcrOptions(force_full_page_ocr=True)
    # ocr_options = TesseractOcrOptions(force_full_page_ocr=True)
    # ocr_options = OcrMacOptions(force_full_page_ocr=True)
    # ocr_options = RapidOcrOptions(force_full_page_ocr=True)
    ocr_options = TesseractCliOcrOptions(force_full_page_ocr=True)
    pipeline_options.ocr_options = ocr_options

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )

    doc = converter.convert(input_doc).document
    md = doc.export_to_markdown()
    print(md)


if __name__ == "__main__":
    main()

```
</content>
</file_22>

<file_23>
<path>examples/hybrid_chunking.ipynb</path>
<content>
```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Hybrid chunking"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Overview"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Hybrid chunking applies tokenization-aware refinements on top of document-based hierarchical chunking.\n",
    "\n",
    "For more details, see [here](../../concepts/chunking#hybrid-chunker)."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Setup"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    }
   ],
   "source": [
    "%pip install -qU docling transformers"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Conversion"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "from docling.document_converter import DocumentConverter\n",
    "\n",
    "DOC_SOURCE = \"../../tests/data/md/wiki.md\"\n",
    "\n",
    "doc = DocumentConverter().convert(source=DOC_SOURCE).document"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Chunking\n",
    "\n",
    "### Basic usage\n",
    "\n",
    "For a basic usage scenario, we can just instantiate a `HybridChunker`, which will use\n",
    "the default parameters."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "from docling.chunking import HybridChunker\n",
    "\n",
    "chunker = HybridChunker()\n",
    "chunk_iter = chunker.chunk(dl_doc=doc)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Note that the text you would typically want to embed is the context-enriched one as\n",
    "returned by the `serialize()` method:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "=== 0 ===\n",
      "chunk.text:\n",
      "'International Business Machines Corporation (using the trademark IBM), nicknamed Big Blue, is an American multinational technology company headquartered in Armonk, New York and present in over 175 countries.\\nIt is a publicly traded company and one of the 30 companies in the Dow Jones Industrial Aver…'\n",
      "chunker.serialize(chunk):\n",
      "'IBM\\nInternational Business Machines Corporation (using the trademark IBM), nicknamed Big Blue, is an American multinational technology company headquartered in Armonk, New York and present in over 175 countries.\\nIt is a publicly traded company and one of the 30 companies in the Dow Jones Industrial …'\n",
      "\n",
      "=== 1 ===\n",
      "chunk.text:\n",
      "'IBM originated with several technological innovations developed and commercialized in the late 19th century. Julius E. Pitrap patented the computing scale in 1885;[17] Alexander Dey invented the dial recorder (1888);[18] Herman Hollerith patented the Electric Tabulating Machine (1889);[19] and Willa…'\n",
      "chunker.serialize(chunk):\n",
      "'IBM\\n1910s–1950s\\nIBM originated with several technological innovations developed and commercialized in the late 19th century. Julius E. Pitrap patented the computing scale in 1885;[17] Alexander Dey invented the dial recorder (1888);[18] Herman Hollerith patented the Electric Tabulating Machine (1889…'\n",
      "\n",
      "=== 2 ===\n",
      "chunk.text:\n",
      "'Collectively, the companies manufactured a wide array of machinery for sale and lease, ranging from commercial scales and industrial time recorders, meat and cheese slicers, to tabulators and punched cards. Thomas J. Watson, Sr., fired from the National Cash Register Company by John Henry Patterson,…'\n",
      "chunker.serialize(chunk):\n",
      "'IBM\\n1910s–1950s\\nCollectively, the companies manufactured a wide array of machinery for sale and lease, ranging from commercial scales and industrial time recorders, meat and cheese slicers, to tabulators and punched cards. Thomas J. Watson, Sr., fired from the National Cash Register Company by John …'\n",
      "\n",
      "=== 3 ===\n",
      "chunk.text:\n",
      "'In 1961, IBM developed the SABRE reservation system for American Airlines and introduced the highly successful Selectric typewriter.…'\n",
      "chunker.serialize(chunk):\n",
      "'IBM\\n1960s–1980s\\nIn 1961, IBM developed the SABRE reservation system for American Airlines and introduced the highly successful Selectric typewriter.…'\n",
      "\n"
     ]
    }
   ],
   "source": [
    "for i, chunk in enumerate(chunk_iter):\n",
    "    print(f\"=== {i} ===\")\n",
    "    print(f\"chunk.text:\\n{repr(f'{chunk.text[:300]}…')}\")\n",
    "\n",
    "    enriched_text = chunker.serialize(chunk=chunk)\n",
    "    print(f\"chunker.serialize(chunk):\\n{repr(f'{enriched_text[:300]}…')}\")\n",
    "\n",
    "    print()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Advanced usage\n",
    "\n",
    "For more control on the chunking, we can parametrize through the `HybridChunker`\n",
    "arguments illustrated below.\n",
    "\n",
    "Notice how `tokenizer` and `embed_model` further below are single-sourced from\n",
    "`EMBED_MODEL_ID`.\n",
    "This is important for making sure the chunker and the embedding model are using the same\n",
    "tokenizer."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "from transformers import AutoTokenizer\n",
    "\n",
    "from docling.chunking import HybridChunker\n",
    "\n",
    "EMBED_MODEL_ID = \"sentence-transformers/all-MiniLM-L6-v2\"\n",
    "MAX_TOKENS = 64  # set to a small number for illustrative purposes\n",
    "\n",
    "tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_ID)\n",
    "\n",
    "chunker = HybridChunker(\n",
    "    tokenizer=tokenizer,  # instance or model name, defaults to \"sentence-transformers/all-MiniLM-L6-v2\"\n",
    "    max_tokens=MAX_TOKENS,  # optional, by default derived from `tokenizer`\n",
    "    merge_peers=True,  # optional, defaults to True\n",
    ")\n",
    "chunk_iter = chunker.chunk(dl_doc=doc)\n",
    "chunks = list(chunk_iter)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Points to notice looking at the output chunks below:\n",
    "- Where possible, we fit the limit of 64 tokens for the metadata-enriched serialization form (see chunk 2)\n",
    "- Where neeeded, we stop before the limit, e.g. see cases of 63 as it would otherwise run into a comma (see chunk 6)\n",
    "- Where possible, we merge undersized peer chunks (see chunk 0)\n",
    "- \"Tail\" chunks trailing right after merges may still be undersized (see chunk 8)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "=== 0 ===\n",
      "chunk.text (55 tokens):\n",
      "'International Business Machines Corporation (using the trademark IBM), nicknamed Big Blue, is an American multinational technology company headquartered in Armonk, New York and present in over 175 countries.\\nIt is a publicly traded company and one of the 30 companies in the Dow Jones Industrial Average.'\n",
      "chunker.serialize(chunk) (56 tokens):\n",
      "'IBM\\nInternational Business Machines Corporation (using the trademark IBM), nicknamed Big Blue, is an American multinational technology company headquartered in Armonk, New York and present in over 175 countries.\\nIt is a publicly traded company and one of the 30 companies in the Dow Jones Industrial Average.'\n",
      "\n",
      "=== 1 ===\n",
      "chunk.text (45 tokens):\n",
      "'IBM is the largest industrial research organization in the world, with 19 research facilities across a dozen countries, having held the record for most annual U.S. patents generated by a business for 29 consecutive years from 1993 to 2021.'\n",
      "chunker.serialize(chunk) (46 tokens):\n",
      "'IBM\\nIBM is the largest industrial research organization in the world, with 19 research facilities across a dozen countries, having held the record for most annual U.S. patents generated by a business for 29 consecutive years from 1993 to 2021.'\n",
      "\n",
      "=== 2 ===\n",
      "chunk.text (63 tokens):\n",
      "'IBM was founded in 1911 as the Computing-Tabulating-Recording Company (CTR), a holding company of manufacturers of record-keeping and measuring systems. It was renamed \"International Business Machines\" in 1924 and soon became the leading manufacturer of punch-card tabulating systems. During the 1960s and 1970s, the'\n",
      "chunker.serialize(chunk) (64 tokens):\n",
      "'IBM\\nIBM was founded in 1911 as the Computing-Tabulating-Recording Company (CTR), a holding company of manufacturers of record-keeping and measuring systems. It was renamed \"International Business Machines\" in 1924 and soon became the leading manufacturer of punch-card tabulating systems. During the 1960s and 1970s, the'\n",
      "\n",
      "=== 3 ===\n",
      "chunk.text (44 tokens):\n",
      "\"IBM mainframe, exemplified by the System/360, was the world's dominant computing platform, with the company producing 80 percent of computers in the U.S. and 70 percent of computers worldwide.[11]\"\n",
      "chunker.serialize(chunk) (45 tokens):\n",
      "\"IBM\\nIBM mainframe, exemplified by the System/360, was the world's dominant computing platform, with the company producing 80 percent of computers in the U.S. and 70 percent of computers worldwide.[11]\"\n",
      "\n",
      "=== 4 ===\n",
      "chunk.text (63 tokens):\n",
      "'IBM debuted in the microcomputer market in 1981 with the IBM Personal Computer, — its DOS software provided by Microsoft, — which became the basis for the majority of personal computers to the present day.[12] The company later also found success in the portable space with the ThinkPad. Since the 1990s,'\n",
      "chunker.serialize(chunk) (64 tokens):\n",
      "'IBM\\nIBM debuted in the microcomputer market in 1981 with the IBM Personal Computer, — its DOS software provided by Microsoft, — which became the basis for the majority of personal computers to the present day.[12] The company later also found success in the portable space with the ThinkPad. Since the 1990s,'\n",
      "\n",
      "=== 5 ===\n",
      "chunk.text (61 tokens):\n",
      "'IBM has concentrated on computer services, software, supercomputers, and scientific research; it sold its microcomputer division to Lenovo in 2005. IBM continues to develop mainframes, and its supercomputers have consistently ranked among the most powerful in the world in the 21st century.'\n",
      "chunker.serialize(chunk) (62 tokens):\n",
      "'IBM\\nIBM has concentrated on computer services, software, supercomputers, and scientific research; it sold its microcomputer division to Lenovo in 2005. IBM continues to develop mainframes, and its supercomputers have consistently ranked among the most powerful in the world in the 21st century.'\n",
      "\n",
      "=== 6 ===\n",
      "chunk.text (62 tokens):\n",
      "\"As one of the world's oldest and largest technology companies, IBM has been responsible for several technological innovations, including the automated teller machine (ATM), dynamic random-access memory (DRAM), the floppy disk, the hard disk drive, the magnetic stripe card, the relational database, the SQL programming\"\n",
      "chunker.serialize(chunk) (63 tokens):\n",
      "\"IBM\\nAs one of the world's oldest and largest technology companies, IBM has been responsible for several technological innovations, including the automated teller machine (ATM), dynamic random-access memory (DRAM), the floppy disk, the hard disk drive, the magnetic stripe card, the relational database, the SQL programming\"\n",
      "\n",
      "=== 7 ===\n",
      "chunk.text (63 tokens):\n",
      "'language, and the UPC barcode. The company has made inroads in advanced computer chips, quantum computing, artificial intelligence, and data infrastructure.[13][14][15] IBM employees and alumni have won various recognitions for their scientific research and inventions, including six Nobel Prizes and six Turing'\n",
      "chunker.serialize(chunk) (64 tokens):\n",
      "'IBM\\nlanguage, and the UPC barcode. The company has made inroads in advanced computer chips, quantum computing, artificial intelligence, and data infrastructure.[13][14][15] IBM employees and alumni have won various recognitions for their scientific research and inventions, including six Nobel Prizes and six Turing'\n",
      "\n",
      "=== 8 ===\n",
      "chunk.text (5 tokens):\n",
      "'Awards.[16]'\n",
      "chunker.serialize(chunk) (6 tokens):\n",
      "'IBM\\nAwards.[16]'\n",
      "\n",
      "=== 9 ===\n",
      "chunk.text (56 tokens):\n",
      "'IBM originated with several technological innovations developed and commercialized in the late 19th century. Julius E. Pitrap patented the computing scale in 1885;[17] Alexander Dey invented the dial recorder (1888);[18] Herman Hollerith patented the Electric Tabulating Machine'\n",
      "chunker.serialize(chunk) (60 tokens):\n",
      "'IBM\\n1910s–1950s\\nIBM originated with several technological innovations developed and commercialized in the late 19th century. Julius E. Pitrap patented the computing scale in 1885;[17] Alexander Dey invented the dial recorder (1888);[18] Herman Hollerith patented the Electric Tabulating Machine'\n",
      "\n",
      "=== 10 ===\n",
      "chunk.text (60 tokens):\n",
      "\"(1889);[19] and Willard Bundy invented a time clock to record workers' arrival and departure times on a paper tape (1889).[20] On June 16, 1911, their four companies were amalgamated in New York State by Charles Ranlett Flint forming a fifth company, the\"\n",
      "chunker.serialize(chunk) (64 tokens):\n",
      "\"IBM\\n1910s–1950s\\n(1889);[19] and Willard Bundy invented a time clock to record workers' arrival and departure times on a paper tape (1889).[20] On June 16, 1911, their four companies were amalgamated in New York State by Charles Ranlett Flint forming a fifth company, the\"\n",
      "\n",
      "=== 11 ===\n",
      "chunk.text (59 tokens):\n",
      "'Computing-Tabulating-Recording Company (CTR) based in Endicott, New York.[1][21] The five companies had 1,300 employees and offices and plants in Endicott and Binghamton, New York; Dayton, Ohio; Detroit, Michigan; Washington,'\n",
      "chunker.serialize(chunk) (63 tokens):\n",
      "'IBM\\n1910s–1950s\\nComputing-Tabulating-Recording Company (CTR) based in Endicott, New York.[1][21] The five companies had 1,300 employees and offices and plants in Endicott and Binghamton, New York; Dayton, Ohio; Detroit, Michigan; Washington,'\n",
      "\n",
      "=== 12 ===\n",
      "chunk.text (13 tokens):\n",
      "'D.C.; and Toronto, Canada.[22]'\n",
      "chunker.serialize(chunk) (17 tokens):\n",
      "'IBM\\n1910s–1950s\\nD.C.; and Toronto, Canada.[22]'\n",
      "\n",
      "=== 13 ===\n",
      "chunk.text (60 tokens):\n",
      "'Collectively, the companies manufactured a wide array of machinery for sale and lease, ranging from commercial scales and industrial time recorders, meat and cheese slicers, to tabulators and punched cards. Thomas J. Watson, Sr., fired from the National Cash Register Company by John Henry Patterson, called'\n",
      "chunker.serialize(chunk) (64 tokens):\n",
      "'IBM\\n1910s–1950s\\nCollectively, the companies manufactured a wide array of machinery for sale and lease, ranging from commercial scales and industrial time recorders, meat and cheese slicers, to tabulators and punched cards. Thomas J. Watson, Sr., fired from the National Cash Register Company by John Henry Patterson, called'\n",
      "\n",
      "=== 14 ===\n",
      "chunk.text (59 tokens):\n",
      "\"on Flint and, in 1914, was offered a position at CTR.[23] Watson joined CTR as general manager and then, 11 months later, was made President when antitrust cases relating to his time at NCR were resolved.[24] Having learned Patterson's pioneering business\"\n",
      "chunker.serialize(chunk) (63 tokens):\n",
      "\"IBM\\n1910s–1950s\\non Flint and, in 1914, was offered a position at CTR.[23] Watson joined CTR as general manager and then, 11 months later, was made President when antitrust cases relating to his time at NCR were resolved.[24] Having learned Patterson's pioneering business\"\n",
      "\n",
      "=== 15 ===\n",
      "chunk.text (23 tokens):\n",
      "\"practices, Watson proceeded to put the stamp of NCR onto CTR's companies.[23]:\\n105\"\n",
      "chunker.serialize(chunk) (27 tokens):\n",
      "\"IBM\\n1910s–1950s\\npractices, Watson proceeded to put the stamp of NCR onto CTR's companies.[23]:\\n105\"\n",
      "\n",
      "=== 16 ===\n",
      "chunk.text (59 tokens):\n",
      "'He implemented sales conventions, \"generous sales incentives, a focus on customer service, an insistence on well-groomed, dark-suited salesmen and had an evangelical fervor for instilling company pride and loyalty in every worker\".[25][26] His favorite slogan,'\n",
      "chunker.serialize(chunk) (63 tokens):\n",
      "'IBM\\n1910s–1950s\\nHe implemented sales conventions, \"generous sales incentives, a focus on customer service, an insistence on well-groomed, dark-suited salesmen and had an evangelical fervor for instilling company pride and loyalty in every worker\".[25][26] His favorite slogan,'\n",
      "\n",
      "=== 17 ===\n",
      "chunk.text (60 tokens):\n",
      "'\"THINK\", became a mantra for each company\\'s employees.[25] During Watson\\'s first four years, revenues reached $9 million ($158 million today) and the company\\'s operations expanded to Europe, South America, Asia and Australia.[25] Watson never liked the'\n",
      "chunker.serialize(chunk) (64 tokens):\n",
      "'IBM\\n1910s–1950s\\n\"THINK\", became a mantra for each company\\'s employees.[25] During Watson\\'s first four years, revenues reached $9 million ($158 million today) and the company\\'s operations expanded to Europe, South America, Asia and Australia.[25] Watson never liked the'\n",
      "\n",
      "=== 18 ===\n",
      "chunk.text (57 tokens):\n",
      "'clumsy hyphenated name \"Computing-Tabulating-Recording Company\" and chose to replace it with the more expansive title \"International Business Machines\" which had previously been used as the name of CTR\\'s Canadian Division;[27] the name was changed on February 14,'\n",
      "chunker.serialize(chunk) (61 tokens):\n",
      "'IBM\\n1910s–1950s\\nclumsy hyphenated name \"Computing-Tabulating-Recording Company\" and chose to replace it with the more expansive title \"International Business Machines\" which had previously been used as the name of CTR\\'s Canadian Division;[27] the name was changed on February 14,'\n",
      "\n",
      "=== 19 ===\n",
      "chunk.text (21 tokens):\n",
      "'1924.[28] By 1933, most of the subsidiaries had been merged into one company, IBM.'\n",
      "chunker.serialize(chunk) (25 tokens):\n",
      "'IBM\\n1910s–1950s\\n1924.[28] By 1933, most of the subsidiaries had been merged into one company, IBM.'\n",
      "\n",
      "=== 20 ===\n",
      "chunk.text (22 tokens):\n",
      "'In 1961, IBM developed the SABRE reservation system for American Airlines and introduced the highly successful Selectric typewriter.'\n",
      "chunker.serialize(chunk) (26 tokens):\n",
      "'IBM\\n1960s–1980s\\nIn 1961, IBM developed the SABRE reservation system for American Airlines and introduced the highly successful Selectric typewriter.'\n",
      "\n"
     ]
    }
   ],
   "source": [
    "for i, chunk in enumerate(chunks):\n",
    "    print(f\"=== {i} ===\")\n",
    "    txt_tokens = len(tokenizer.tokenize(chunk.text, max_length=None))\n",
    "    print(f\"chunk.text ({txt_tokens} tokens):\\n{repr(chunk.text)}\")\n",
    "\n",
    "    ser_txt = chunker.serialize(chunk=chunk)\n",
    "    ser_tokens = len(tokenizer.tokenize(ser_txt, max_length=None))\n",
    "    print(f\"chunker.serialize(chunk) ({ser_tokens} tokens):\\n{repr(ser_txt)}\")\n",
    "\n",
    "    print()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

```
</content>
</file_23>

<file_24>
<path>examples/index.md</path>
<content>
```markdown
Use the navigation on the left to browse through examples covering a range of possible workflows and use cases.

```
</content>
</file_24>

<file_25>
<path>examples/inspect_picture_content.py</path>
<content>
```python
from docling_core.types.doc import TextItem

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

source = "tests/data/amt_handbook_sample.pdf"

pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = 2
pipeline_options.generate_page_images = True

doc_converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

result = doc_converter.convert(source)

doc = result.document

for picture in doc.pictures:
    # picture.get_image(doc).show() # display the picture
    print(picture.caption_text(doc), " contains these elements:")

    for item, level in doc.iterate_items(root=picture, traverse_pictures=True):
        if isinstance(item, TextItem):
            print(item.text)

    print("\n")

```
</content>
</file_25>

<file_26>
<path>examples/minimal.py</path>
<content>
```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())
# output: ## Docling Technical Report [...]"

```
</content>
</file_26>

<file_27>
<path>examples/rag_azuresearch.ipynb</path>
<content>
```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "Ag9kcX2B_atc"
   },
   "source": [
    "<a href=\"https://colab.research.google.com/github/DS4SD/docling/blob/main/docs/examples/rag_azuresearch.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# RAG with Azure AI Search"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "\n",
    "| Step               | Tech               | Execution |\n",
    "| ------------------ | ------------------ | --------- |\n",
    "| Embedding          | Azure OpenAI       | 🌐 Remote |\n",
    "| Vector Store       | Azure AI Search    | 🌐 Remote |\n",
    "| Gen AI  | Azure OpenAI | 🌐 Remote |"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "\n",
    "## A recipe 🧑‍🍳 🐥 💚\n",
    "\n",
    "This notebook demonstrates how to build a Retrieval-Augmented Generation (RAG) system using:\n",
    "- [Docling](https://ds4sd.github.io/docling/) for document parsing and chunking\n",
    "- [Azure AI Search](https://azure.microsoft.com/products/ai-services/ai-search/?msockid=0109678bea39665431e37323ebff6723) for vector indexing and retrieval\n",
    "- [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service?msockid=0109678bea39665431e37323ebff6723) for embeddings and chat completion\n",
    "\n",
    "This sample demonstrates how to:\n",
    "1. Parse a PDF with Docling.\n",
    "2. Chunk the parsed text.\n",
    "3. Use Azure OpenAI for embeddings.\n",
    "4. Index and search in Azure AI Search.\n",
    "5. Run a retrieval-augmented generation (RAG) query with Azure OpenAI GPT-4o.\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# If running in a fresh environment (like Google Colab), uncomment and run this single command:\n",
    "%pip install \"docling~=2.12\" azure-search-documents==11.5.2 azure-identity openai rich torch python-dotenv"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Part 0: Prerequisites\n",
    " - **Azure AI Search** resource\n",
    " - **Azure OpenAI** resource with a deployed embedding and chat completion model (e.g. `text-embedding-3-small` and `gpt-4o`) \n",
    " - **Docling 2.12+** (installs `docling_core` automatically)  Docling installed (Python 3.8+ environment)\n",
    "\n",
    "- A **GPU-enabled environment** is preferred for faster parsing. Docling 2.12 automatically detects GPU if present.\n",
    "  - If you only have CPU, parsing large PDFs can be slower.  "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "load_dotenv()\n",
    "\n",
    "\n",
    "def _get_env(key, default=None):\n",
    "    try:\n",
    "        from google.colab import userdata\n",
    "\n",
    "        try:\n",
    "            return userdata.get(key)\n",
    "        except userdata.SecretNotFoundError:\n",
    "            pass\n",
    "    except ImportError:\n",
    "        pass\n",
    "    return os.getenv(key, default)\n",
    "\n",
    "\n",
    "AZURE_SEARCH_ENDPOINT = _get_env(\"AZURE_SEARCH_ENDPOINT\")\n",
    "AZURE_SEARCH_KEY = _get_env(\"AZURE_SEARCH_KEY\")  # Ensure this is your Admin Key\n",
    "AZURE_SEARCH_INDEX_NAME = _get_env(\"AZURE_SEARCH_INDEX_NAME\", \"docling-rag-sample\")\n",
    "AZURE_OPENAI_ENDPOINT = _get_env(\"AZURE_OPENAI_ENDPOINT\")\n",
    "AZURE_OPENAI_API_KEY = _get_env(\"AZURE_OPENAI_API_KEY\")\n",
    "AZURE_OPENAI_API_VERSION = _get_env(\"AZURE_OPENAI_API_VERSION\", \"2024-10-21\")\n",
    "AZURE_OPENAI_CHAT_MODEL = _get_env(\n",
    "    \"AZURE_OPENAI_CHAT_MODEL\"\n",
    ")  # Using a deployed model named \"gpt-4o\"\n",
    "AZURE_OPENAI_EMBEDDINGS = _get_env(\n",
    "    \"AZURE_OPENAI_EMBEDDINGS\", \"text-embedding-3-small\"\n",
    ")  # Using a deployed model named \"text-embeddings-3-small\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Part 1: Parse the PDF with Docling\n",
    "\n",
    "We’ll parse the **Microsoft GraphRAG Research Paper** (~15 pages). Parsing should be relatively quick, even on CPU, but it will be faster on a GPU or MPS device if available.\n",
    "\n",
    "*(If you prefer a different document, simply provide a different URL or local file path.)*"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #808000; text-decoration-color: #808000; font-weight: bold\">Parsing a ~</span><span style=\"color: #808000; text-decoration-color: #808000; font-weight: bold\">15</span><span style=\"color: #808000; text-decoration-color: #808000; font-weight: bold\">-page PDF. The process should be relatively quick, even on CPU...</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;33mParsing a ~\u001b[0m\u001b[1;33m15\u001b[0m\u001b[1;33m-page PDF. The process should be relatively quick, even on CPU\u001b[0m\u001b[1;33m...\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\">╭─────────────────────────────────────────── Docling Markdown Preview ────────────────────────────────────────────╮\n",
       "│ ## From Local to Global: A Graph RAG Approach to Query-Focused Summarization                                    │\n",
       "│                                                                                                                 │\n",
       "│ Darren Edge 1†                                                                                                  │\n",
       "│                                                                                                                 │\n",
       "│ Ha Trinh 1†                                                                                                     │\n",
       "│                                                                                                                 │\n",
       "│ Newman Cheng 2                                                                                                  │\n",
       "│                                                                                                                 │\n",
       "│ Joshua Bradley 2                                                                                                │\n",
       "│                                                                                                                 │\n",
       "│ Alex Chao 3                                                                                                     │\n",
       "│                                                                                                                 │\n",
       "│ Apurva Mody 3                                                                                                   │\n",
       "│                                                                                                                 │\n",
       "│ Steven Truitt 2                                                                                                 │\n",
       "│                                                                                                                 │\n",
       "│ ## Jonathan Larson 1                                                                                            │\n",
       "│                                                                                                                 │\n",
       "│ 1 Microsoft Research 2 Microsoft Strategic Missions and Technologies 3 Microsoft Office of the CTO              │\n",
       "│                                                                                                                 │\n",
       "│ { daedge,trinhha,newmancheng,joshbradley,achao,moapurva,steventruitt,jolarso } @microsoft.com                   │\n",
       "│                                                                                                                 │\n",
       "│ † These authors contributed equally to this work                                                                │\n",
       "│                                                                                                                 │\n",
       "│ ## Abstract                                                                                                     │\n",
       "│                                                                                                                 │\n",
       "│ The use of retrieval-augmented gen...                                                                           │\n",
       "╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\n",
       "</pre>\n"
      ],
      "text/plain": [
       "╭─────────────────────────────────────────── Docling Markdown Preview ────────────────────────────────────────────╮\n",
       "│ ## From Local to Global: A Graph RAG Approach to Query-Focused Summarization                                    │\n",
       "│                                                                                                                 │\n",
       "│ Darren Edge 1†                                                                                                  │\n",
       "│                                                                                                                 │\n",
       "│ Ha Trinh 1†                                                                                                     │\n",
       "│                                                                                                                 │\n",
       "│ Newman Cheng 2                                                                                                  │\n",
       "│                                                                                                                 │\n",
       "│ Joshua Bradley 2                                                                                                │\n",
       "│                                                                                                                 │\n",
       "│ Alex Chao 3                                                                                                     │\n",
       "│                                                                                                                 │\n",
       "│ Apurva Mody 3                                                                                                   │\n",
       "│                                                                                                                 │\n",
       "│ Steven Truitt 2                                                                                                 │\n",
       "│                                                                                                                 │\n",
       "│ ## Jonathan Larson 1                                                                                            │\n",
       "│                                                                                                                 │\n",
       "│ 1 Microsoft Research 2 Microsoft Strategic Missions and Technologies 3 Microsoft Office of the CTO              │\n",
       "│                                                                                                                 │\n",
       "│ { daedge,trinhha,newmancheng,joshbradley,achao,moapurva,steventruitt,jolarso } @microsoft.com                   │\n",
       "│                                                                                                                 │\n",
       "│ † These authors contributed equally to this work                                                                │\n",
       "│                                                                                                                 │\n",
       "│ ## Abstract                                                                                                     │\n",
       "│                                                                                                                 │\n",
       "│ The use of retrieval-augmented gen...                                                                           │\n",
       "╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from rich.console import Console\n",
    "from rich.panel import Panel\n",
    "\n",
    "from docling.document_converter import DocumentConverter\n",
    "\n",
    "console = Console()\n",
    "\n",
    "# This URL points to the Microsoft GraphRAG Research Paper (arXiv: 2404.16130), ~15 pages\n",
    "source_url = \"https://arxiv.org/pdf/2404.16130\"\n",
    "\n",
    "console.print(\n",
    "    \"[bold yellow]Parsing a ~15-page PDF. The process should be relatively quick, even on CPU...[/bold yellow]\"\n",
    ")\n",
    "converter = DocumentConverter()\n",
    "result = converter.convert(source_url)\n",
    "\n",
    "# Optional: preview the parsed Markdown\n",
    "md_preview = result.document.export_to_markdown()\n",
    "console.print(Panel(md_preview[:500] + \"...\", title=\"Docling Markdown Preview\"))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Part 2: Hierarchical Chunking\n",
    "We convert the `Document` into smaller chunks for embedding and indexing. The built-in `HierarchicalChunker` preserves structure. "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\">Total chunks from PDF: <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">106</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "Total chunks from PDF: \u001b[1;36m106\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from docling.chunking import HierarchicalChunker\n",
    "\n",
    "chunker = HierarchicalChunker()\n",
    "doc_chunks = list(chunker.chunk(result.document))\n",
    "\n",
    "all_chunks = []\n",
    "for idx, c in enumerate(doc_chunks):\n",
    "    chunk_text = c.text\n",
    "    all_chunks.append((f\"chunk_{idx}\", chunk_text))\n",
    "\n",
    "console.print(f\"Total chunks from PDF: {len(all_chunks)}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Part 3: Create Azure AI Search Index and Push Chunk Embeddings\n",
    "We’ll define a vector index in Azure AI Search, then embed each chunk using Azure OpenAI and upload in batches."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\">Index <span style=\"color: #008000; text-decoration-color: #008000\">'docling-rag-sample-2'</span> created.\n",
       "</pre>\n"
      ],
      "text/plain": [
       "Index \u001b[32m'docling-rag-sample-2'\u001b[0m created.\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from azure.core.credentials import AzureKeyCredential\n",
    "from azure.search.documents.indexes import SearchIndexClient\n",
    "from azure.search.documents.indexes.models import (\n",
    "    AzureOpenAIVectorizer,\n",
    "    AzureOpenAIVectorizerParameters,\n",
    "    HnswAlgorithmConfiguration,\n",
    "    SearchableField,\n",
    "    SearchField,\n",
    "    SearchFieldDataType,\n",
    "    SearchIndex,\n",
    "    SimpleField,\n",
    "    VectorSearch,\n",
    "    VectorSearchProfile,\n",
    ")\n",
    "from rich.console import Console\n",
    "\n",
    "console = Console()\n",
    "\n",
    "VECTOR_DIM = 1536  # Adjust based on your chosen embeddings model\n",
    "\n",
    "index_client = SearchIndexClient(\n",
    "    AZURE_SEARCH_ENDPOINT, AzureKeyCredential(AZURE_SEARCH_KEY)\n",
    ")\n",
    "\n",
    "\n",
    "def create_search_index(index_name: str):\n",
    "    # Define fields\n",
    "    fields = [\n",
    "        SimpleField(name=\"chunk_id\", type=SearchFieldDataType.String, key=True),\n",
    "        SearchableField(name=\"content\", type=SearchFieldDataType.String),\n",
    "        SearchField(\n",
    "            name=\"content_vector\",\n",
    "            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),\n",
    "            searchable=True,\n",
    "            filterable=False,\n",
    "            sortable=False,\n",
    "            facetable=False,\n",
    "            vector_search_dimensions=VECTOR_DIM,\n",
    "            vector_search_profile_name=\"default\",\n",
    "        ),\n",
    "    ]\n",
    "    # Vector search config with an AzureOpenAIVectorizer\n",
    "    vector_search = VectorSearch(\n",
    "        algorithms=[HnswAlgorithmConfiguration(name=\"default\")],\n",
    "        profiles=[\n",
    "            VectorSearchProfile(\n",
    "                name=\"default\",\n",
    "                algorithm_configuration_name=\"default\",\n",
    "                vectorizer_name=\"default\",\n",
    "            )\n",
    "        ],\n",
    "        vectorizers=[\n",
    "            AzureOpenAIVectorizer(\n",
    "                vectorizer_name=\"default\",\n",
    "                parameters=AzureOpenAIVectorizerParameters(\n",
    "                    resource_url=AZURE_OPENAI_ENDPOINT,\n",
    "                    deployment_name=AZURE_OPENAI_EMBEDDINGS,\n",
    "                    model_name=\"text-embedding-3-small\",\n",
    "                    api_key=AZURE_OPENAI_API_KEY,\n",
    "                ),\n",
    "            )\n",
    "        ],\n",
    "    )\n",
    "\n",
    "    # Create or update the index\n",
    "    new_index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)\n",
    "    try:\n",
    "        index_client.delete_index(index_name)\n",
    "    except:\n",
    "        pass\n",
    "\n",
    "    index_client.create_or_update_index(new_index)\n",
    "    console.print(f\"Index '{index_name}' created.\")\n",
    "\n",
    "\n",
    "create_search_index(AZURE_SEARCH_INDEX_NAME)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "#### Generate Embeddings and Upload to Azure AI Search\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\">Uploaded batch <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">0</span> -&gt; <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">50</span>; all_succeeded: <span style=\"color: #00ff00; text-decoration-color: #00ff00; font-style: italic\">True</span>, first_doc_status_code: <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">201</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "Uploaded batch \u001b[1;36m0\u001b[0m -> \u001b[1;36m50\u001b[0m; all_succeeded: \u001b[3;92mTrue\u001b[0m, first_doc_status_code: \u001b[1;36m201\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\">Uploaded batch <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">50</span> -&gt; <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">100</span>; all_succeeded: <span style=\"color: #00ff00; text-decoration-color: #00ff00; font-style: italic\">True</span>, first_doc_status_code: <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">201</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "Uploaded batch \u001b[1;36m50\u001b[0m -> \u001b[1;36m100\u001b[0m; all_succeeded: \u001b[3;92mTrue\u001b[0m, first_doc_status_code: \u001b[1;36m201\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\">Uploaded batch <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">100</span> -&gt; <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">106</span>; all_succeeded: <span style=\"color: #00ff00; text-decoration-color: #00ff00; font-style: italic\">True</span>, first_doc_status_code: <span style=\"color: #008080; text-decoration-color: #008080; font-weight: bold\">201</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "Uploaded batch \u001b[1;36m100\u001b[0m -> \u001b[1;36m106\u001b[0m; all_succeeded: \u001b[3;92mTrue\u001b[0m, first_doc_status_code: \u001b[1;36m201\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\">All chunks uploaded to Azure Search.\n",
       "</pre>\n"
      ],
      "text/plain": [
       "All chunks uploaded to Azure Search.\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from azure.search.documents import SearchClient\n",
    "from openai import AzureOpenAI\n",
    "\n",
    "search_client = SearchClient(\n",
    "    AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_INDEX_NAME, AzureKeyCredential(AZURE_SEARCH_KEY)\n",
    ")\n",
    "openai_client = AzureOpenAI(\n",
    "    api_key=AZURE_OPENAI_API_KEY,\n",
    "    api_version=AZURE_OPENAI_API_VERSION,\n",
    "    azure_endpoint=AZURE_OPENAI_ENDPOINT,\n",
    ")\n",
    "\n",
    "\n",
    "def embed_text(text: str):\n",
    "    \"\"\"\n",
    "    Helper to generate embeddings with Azure OpenAI.\n",
    "    \"\"\"\n",
    "    response = openai_client.embeddings.create(\n",
    "        input=text, model=AZURE_OPENAI_EMBEDDINGS\n",
    "    )\n",
    "    return response.data[0].embedding\n",
    "\n",
    "\n",
    "upload_docs = []\n",
    "for chunk_id, chunk_text in all_chunks:\n",
    "    embedding_vector = embed_text(chunk_text)\n",
    "    upload_docs.append(\n",
    "        {\n",
    "            \"chunk_id\": chunk_id,\n",
    "            \"content\": chunk_text,\n",
    "            \"content_vector\": embedding_vector,\n",
    "        }\n",
    "    )\n",
    "\n",
    "\n",
    "BATCH_SIZE = 50\n",
    "for i in range(0, len(upload_docs), BATCH_SIZE):\n",
    "    subset = upload_docs[i : i + BATCH_SIZE]\n",
    "    resp = search_client.upload_documents(documents=subset)\n",
    "\n",
    "    all_succeeded = all(r.succeeded for r in resp)\n",
    "    console.print(\n",
    "        f\"Uploaded batch {i} -> {i+len(subset)}; all_succeeded: {all_succeeded}, \"\n",
    "        f\"first_doc_status_code: {resp[0].status_code}\"\n",
    "    )\n",
    "\n",
    "console.print(\"All chunks uploaded to Azure Search.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Part 4: Perform RAG over PDF\n",
    "Combine retrieval from Azure AI Search with Azure OpenAI Chat Completions (aka. grounding your LLM)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">╭──────────────────────────────────────────────────</span> RAG Prompt <span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">───────────────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ You are an AI assistant helping answering questions about Microsoft GraphRAG.                                   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Use ONLY the text below to answer the user's question.                                                          │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ If the answer isn't in the text, say you don't know.                                                            │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Context:                                                                                                        │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Community summaries vs. source texts. When comparing community summaries to source texts using Graph RAG,       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ community summaries generally provided a small but consistent improvement in answer comprehensiveness and       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ diversity, except for root-level summaries. Intermediate-level summaries in the Podcast dataset and low-level   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ community summaries in the News dataset achieved comprehensiveness win rates of 57% and 64%, respectively.      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Diversity win rates were 57% for Podcast intermediate-level summaries and 60% for News low-level community      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ summaries. Table 3 also illustrates the scalability advantages of Graph RAG compared to source text             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ summarization: for low-level community summaries ( C3 ), Graph RAG required 26-33% fewer context tokens, while  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ for root-level community summaries ( C0 ), it required over 97% fewer tokens. For a modest drop in performance  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ compared with other global methods, root-level Graph RAG offers a highly efficient method for the iterative     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ question answering that characterizes sensemaking activity, while retaining advantages in comprehensiveness     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ (72% win rate) and diversity (62% win rate) over na¨ıve RAG.                                                    │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ We have presented a global approach to Graph RAG, combining knowledge graph generation, retrieval-augmented     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ generation (RAG), and query-focused summarization (QFS) to support human sensemaking over entire text corpora.  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Initial evaluations show substantial improvements over a na¨ıve RAG baseline for both the comprehensiveness and │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ diversity of answers, as well as favorable comparisons to a global but graph-free approach using map-reduce     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ source text summarization. For situations requiring many global queries over the same dataset, summaries of     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ root-level communities in the entity-based graph index provide a data index that is both superior to na¨ıve RAG │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ and achieves competitive performance to other global methods at a fraction of the token cost.                   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Trade-offs of building a graph index . We consistently observed Graph RAG achieve the best headto-head results  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ against other methods, but in many cases the graph-free approach to global summarization of source texts        │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ performed competitively. The real-world decision about whether to invest in building a graph index depends on   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ multiple factors, including the compute budget, expected number of lifetime queries per dataset, and value      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ obtained from other aspects of the graph index (including the generic community summaries and the use of other  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ graph-related RAG approaches).                                                                                  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Future work . The graph index, rich text annotations, and hierarchical community structure supporting the       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ current Graph RAG approach offer many possibilities for refinement and adaptation. This includes RAG approaches │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ that operate in a more local manner, via embedding-based matching of user queries and graph annotations, as     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ well as the possibility of hybrid RAG schemes that combine embedding-based matching against community reports   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ before employing our map-reduce summarization mechanisms. This 'roll-up' operation could also be extended       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ across more levels of the community hierarchy, as well as implemented as a more exploratory 'drill down'        │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ mechanism that follows the information scent contained in higher-level community summaries.                     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Advanced RAG systems include pre-retrieval, retrieval, post-retrieval strategies designed to overcome the       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ drawbacks of Na¨ıve RAG, while Modular RAG systems include patterns for iterative and dynamic cycles of         │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ interleaved retrieval and generation (Gao et al., 2023). Our implementation of Graph RAG incorporates multiple  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ concepts related to other systems. For example, our community summaries are a kind of self-memory (Selfmem,     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Cheng et al., 2024) for generation-augmented retrieval (GAR, Mao et al., 2020) that facilitates future          │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ generation cycles, while our parallel generation of community answers from these summaries is a kind of         │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ iterative (Iter-RetGen, Shao et al., 2023) or federated (FeB4RAG, Wang et al., 2024) retrieval-generation       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ strategy. Other systems have also combined these concepts for multi-document summarization (CAiRE-COVID, Su et  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ al., 2020) and multi-hop question answering (ITRG, Feng et al., 2023; IR-CoT, Trivedi et al., 2022; DSP,        │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Khattab et al., 2022). Our use of a hierarchical index and summarization also bears resemblance to further      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ approaches, such as generating a hierarchical index of text chunks by clustering the vectors of text embeddings │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ (RAPTOR, Sarthi et al., 2024) or generating a 'tree of clarifications' to answer multiple interpretations of    │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ambiguous questions (Kim et al., 2023). However, none of these iterative or hierarchical approaches use the     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ kind of self-generated graph index that enables Graph RAG.                                                      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ The use of retrieval-augmented generation (RAG) to retrieve relevant information from an external knowledge     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ source enables large language models (LLMs) to answer questions over private and/or previously unseen document  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ collections. However, RAG fails on global questions directed at an entire text corpus, such as 'What are the    │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ main themes in the dataset?', since this is inherently a queryfocused summarization (QFS) task, rather than an  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ explicit retrieval task. Prior QFS methods, meanwhile, fail to scale to the quantities of text indexed by       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ typical RAGsystems. To combine the strengths of these contrasting methods, we propose a Graph RAG approach to   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ question answering over private text corpora that scales with both the generality of user questions and the     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ quantity of source text to be indexed. Our approach uses an LLM to build a graph-based text index in two        │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ stages: first to derive an entity knowledge graph from the source documents, then to pregenerate community      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ summaries for all groups of closely-related entities. Given a question, each community summary is used to       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ generate a partial response, before all partial responses are again summarized in a final response to the user. │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ For a class of global sensemaking questions over datasets in the 1 million token range, we show that Graph RAG  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ leads to substantial improvements over a na¨ıve RAG baseline for both the comprehensiveness and diversity of    │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ generated answers. An open-source, Python-based implementation of both global and local Graph RAG approaches is │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ forthcoming at https://aka . ms/graphrag .                                                                      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Given the multi-stage nature of our Graph RAG mechanism, the multiple conditions we wanted to compare, and the  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ lack of gold standard answers to our activity-based sensemaking questions, we decided to adopt a head-to-head   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ comparison approach using an LLM evaluator. We selected three target metrics capturing qualities that are       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ desirable for sensemaking activities, as well as a control metric (directness) used as a indicator of validity. │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Since directness is effectively in opposition to comprehensiveness and diversity, we would not expect any       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ method to win across all four metrics.                                                                          │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Figure 1: Graph RAG pipeline using an LLM-derived graph index of source document text. This index spans nodes   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ (e.g., entities), edges (e.g., relationships), and covariates (e.g., claims) that have been detected,           │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ extracted, and summarized by LLM prompts tailored to the domain of the dataset. Community detection (e.g.,      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Leiden, Traag et al., 2019) is used to partition the graph index into groups of elements (nodes, edges,         │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ covariates) that the LLM can summarize in parallel at both indexing time and query time. The 'global answer' to │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ a given query is produced using a final round of query-focused summarization over all community summaries       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ reporting relevance to that query.                                                                              │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Retrieval-augmented generation (RAG, Lewis et al., 2020) is an established approach to answering user questions │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ over entire datasets, but it is designed for situations where these answers are contained locally within        │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ regions of text whose retrieval provides sufficient grounding for the generation task. Instead, a more          │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ appropriate task framing is query-focused summarization (QFS, Dang, 2006), and in particular, query-focused     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ abstractive summarization that generates natural language summaries and not just concatenated excerpts (Baumel  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ et al., 2018; Laskar et al., 2020; Yao et al., 2017) . In recent years, however, such distinctions between      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ summarization tasks that are abstractive versus extractive, generic versus query-focused, and single-document   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ versus multi-document, have become less relevant. While early applications of the transformer architecture      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ showed substantial improvements on the state-of-the-art for all such summarization tasks (Goodwin et al., 2020; │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Laskar et al., 2022; Liu and Lapata, 2019), these tasks are now trivialized by modern LLMs, including the GPT   │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ (Achiam et al., 2023; Brown et al., 2020), Llama (Touvron et al., 2023), and Gemini (Anil et al., 2023) series, │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ all of which can use in-context learning to summarize any content provided in their context window.             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ ---                                                                                                             │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ community descriptions provide complete coverage of the underlying graph index and the input documents it       │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ represents. Query-focused summarization of an entire corpus is then made possible using a map-reduce approach:  │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ first using each community summary to answer the query independently and in parallel, then summarizing all      │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ relevant partial answers into a final global answer.                                                            │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Question: What are the main advantages of using the Graph RAG approach for query-focused summarization compared │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ to traditional RAG methods?                                                                                     │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│ Answer:                                                                                                         │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;31m╭─\u001b[0m\u001b[1;31m─────────────────────────────────────────────────\u001b[0m RAG Prompt \u001b[1;31m──────────────────────────────────────────────────\u001b[0m\u001b[1;31m─╮\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m                                                                                                               \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mYou are an AI assistant helping answering questions about Microsoft GraphRAG.\u001b[0m\u001b[1;31m                                  \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mUse ONLY the text below to answer the user's question.\u001b[0m\u001b[1;31m                                                         \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mIf the answer isn't in the text, say you don't know.\u001b[0m\u001b[1;31m                                                           \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m                                                                                                               \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mContext:\u001b[0m\u001b[1;31m                                                                                                       \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mCommunity summaries vs. source texts. When comparing community summaries to source texts using Graph RAG, \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mcommunity summaries generally provided a small but consistent improvement in answer comprehensiveness and \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mdiversity, except for root-level summaries. Intermediate-level summaries in the Podcast dataset and low-level \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mcommunity summaries in the News dataset achieved comprehensiveness win rates of 57% and 64%, respectively. \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mDiversity win rates were 57% for Podcast intermediate-level summaries and 60% for News low-level community \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31msummaries. Table 3 also illustrates the scalability advantages of Graph RAG compared to source text \u001b[0m\u001b[1;31m           \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31msummarization: for low-level community summaries ( C3 ), Graph RAG required 26-33% fewer context tokens, while \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mfor root-level community summaries ( C0 ), it required over 97% fewer tokens. For a modest drop in performance \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mcompared with other global methods, root-level Graph RAG offers a highly efficient method for the iterative \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mquestion answering that characterizes sensemaking activity, while retaining advantages in comprehensiveness \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m(72% win rate) and diversity (62% win rate) over na¨ıve RAG.\u001b[0m\u001b[1;31m                                                   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mWe have presented a global approach to Graph RAG, combining knowledge graph generation, retrieval-augmented \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mgeneration (RAG), and query-focused summarization (QFS) to support human sensemaking over entire text corpora. \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mInitial evaluations show substantial improvements over a na¨ıve RAG baseline for both the comprehensiveness and\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mdiversity of answers, as well as favorable comparisons to a global but graph-free approach using map-reduce \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31msource text summarization. For situations requiring many global queries over the same dataset, summaries of \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mroot-level communities in the entity-based graph index provide a data index that is both superior to na¨ıve RAG\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mand achieves competitive performance to other global methods at a fraction of the token cost.\u001b[0m\u001b[1;31m                  \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mTrade-offs of building a graph index . We consistently observed Graph RAG achieve the best headto-head results \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31magainst other methods, but in many cases the graph-free approach to global summarization of source texts \u001b[0m\u001b[1;31m      \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mperformed competitively. The real-world decision about whether to invest in building a graph index depends on \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mmultiple factors, including the compute budget, expected number of lifetime queries per dataset, and value \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mobtained from other aspects of the graph index (including the generic community summaries and the use of other \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mgraph-related RAG approaches).\u001b[0m\u001b[1;31m                                                                                 \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mFuture work . The graph index, rich text annotations, and hierarchical community structure supporting the \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mcurrent Graph RAG approach offer many possibilities for refinement and adaptation. This includes RAG approaches\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mthat operate in a more local manner, via embedding-based matching of user queries and graph annotations, as \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mwell as the possibility of hybrid RAG schemes that combine embedding-based matching against community reports \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mbefore employing our map-reduce summarization mechanisms. This 'roll-up' operation could also be extended \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31macross more levels of the community hierarchy, as well as implemented as a more exploratory 'drill down' \u001b[0m\u001b[1;31m      \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mmechanism that follows the information scent contained in higher-level community summaries.\u001b[0m\u001b[1;31m                    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mAdvanced RAG systems include pre-retrieval, retrieval, post-retrieval strategies designed to overcome the \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mdrawbacks of Na¨ıve RAG, while Modular RAG systems include patterns for iterative and dynamic cycles of \u001b[0m\u001b[1;31m       \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31minterleaved retrieval and generation (Gao et al., 2023). Our implementation of Graph RAG incorporates multiple \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mconcepts related to other systems. For example, our community summaries are a kind of self-memory (Selfmem, \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mCheng et al., 2024) for generation-augmented retrieval (GAR, Mao et al., 2020) that facilitates future \u001b[0m\u001b[1;31m        \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mgeneration cycles, while our parallel generation of community answers from these summaries is a kind of \u001b[0m\u001b[1;31m       \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31miterative (Iter-RetGen, Shao et al., 2023) or federated (FeB4RAG, Wang et al., 2024) retrieval-generation \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mstrategy. Other systems have also combined these concepts for multi-document summarization (CAiRE-COVID, Su et \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mal., 2020) and multi-hop question answering (ITRG, Feng et al., 2023; IR-CoT, Trivedi et al., 2022; DSP, \u001b[0m\u001b[1;31m      \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mKhattab et al., 2022). Our use of a hierarchical index and summarization also bears resemblance to further \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mapproaches, such as generating a hierarchical index of text chunks by clustering the vectors of text embeddings\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m(RAPTOR, Sarthi et al., 2024) or generating a 'tree of clarifications' to answer multiple interpretations of \u001b[0m\u001b[1;31m  \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mambiguous questions (Kim et al., 2023). However, none of these iterative or hierarchical approaches use the \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mkind of self-generated graph index that enables Graph RAG.\u001b[0m\u001b[1;31m                                                     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mThe use of retrieval-augmented generation (RAG) to retrieve relevant information from an external knowledge \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31msource enables large language models (LLMs) to answer questions over private and/or previously unseen document \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mcollections. However, RAG fails on global questions directed at an entire text corpus, such as 'What are the \u001b[0m\u001b[1;31m  \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mmain themes in the dataset?', since this is inherently a queryfocused summarization (QFS) task, rather than an \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mexplicit retrieval task. Prior QFS methods, meanwhile, fail to scale to the quantities of text indexed by \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mtypical RAGsystems. To combine the strengths of these contrasting methods, we propose a Graph RAG approach to \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mquestion answering over private text corpora that scales with both the generality of user questions and the \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mquantity of source text to be indexed. Our approach uses an LLM to build a graph-based text index in two \u001b[0m\u001b[1;31m      \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mstages: first to derive an entity knowledge graph from the source documents, then to pregenerate community \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31msummaries for all groups of closely-related entities. Given a question, each community summary is used to \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mgenerate a partial response, before all partial responses are again summarized in a final response to the user.\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mFor a class of global sensemaking questions over datasets in the 1 million token range, we show that Graph RAG \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mleads to substantial improvements over a na¨ıve RAG baseline for both the comprehensiveness and diversity of \u001b[0m\u001b[1;31m  \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mgenerated answers. An open-source, Python-based implementation of both global and local Graph RAG approaches is\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mforthcoming at https://aka . ms/graphrag .\u001b[0m\u001b[1;31m                                                                     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mGiven the multi-stage nature of our Graph RAG mechanism, the multiple conditions we wanted to compare, and the \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mlack of gold standard answers to our activity-based sensemaking questions, we decided to adopt a head-to-head \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mcomparison approach using an LLM evaluator. We selected three target metrics capturing qualities that are \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mdesirable for sensemaking activities, as well as a control metric (directness) used as a indicator of validity.\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mSince directness is effectively in opposition to comprehensiveness and diversity, we would not expect any \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mmethod to win across all four metrics.\u001b[0m\u001b[1;31m                                                                         \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mFigure 1: Graph RAG pipeline using an LLM-derived graph index of source document text. This index spans nodes \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m(e.g., entities), edges (e.g., relationships), and covariates (e.g., claims) that have been detected, \u001b[0m\u001b[1;31m         \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mextracted, and summarized by LLM prompts tailored to the domain of the dataset. Community detection (e.g., \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mLeiden, Traag et al., 2019) is used to partition the graph index into groups of elements (nodes, edges, \u001b[0m\u001b[1;31m       \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mcovariates) that the LLM can summarize in parallel at both indexing time and query time. The 'global answer' to\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31ma given query is produced using a final round of query-focused summarization over all community summaries \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mreporting relevance to that query.\u001b[0m\u001b[1;31m                                                                             \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mRetrieval-augmented generation (RAG, Lewis et al., 2020) is an established approach to answering user questions\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mover entire datasets, but it is designed for situations where these answers are contained locally within \u001b[0m\u001b[1;31m      \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mregions of text whose retrieval provides sufficient grounding for the generation task. Instead, a more \u001b[0m\u001b[1;31m        \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mappropriate task framing is query-focused summarization (QFS, Dang, 2006), and in particular, query-focused \u001b[0m\u001b[1;31m   \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mabstractive summarization that generates natural language summaries and not just concatenated excerpts (Baumel \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31met al., 2018; Laskar et al., 2020; Yao et al., 2017) . In recent years, however, such distinctions between \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31msummarization tasks that are abstractive versus extractive, generic versus query-focused, and single-document \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mversus multi-document, have become less relevant. While early applications of the transformer architecture \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mshowed substantial improvements on the state-of-the-art for all such summarization tasks (Goodwin et al., 2020;\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mLaskar et al., 2022; Liu and Lapata, 2019), these tasks are now trivialized by modern LLMs, including the GPT \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m(Achiam et al., 2023; Brown et al., 2020), Llama (Touvron et al., 2023), and Gemini (Anil et al., 2023) series,\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mall of which can use in-context learning to summarize any content provided in their context window.\u001b[0m\u001b[1;31m            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m---\u001b[0m\u001b[1;31m                                                                                                            \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mcommunity descriptions provide complete coverage of the underlying graph index and the input documents it \u001b[0m\u001b[1;31m     \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mrepresents. Query-focused summarization of an entire corpus is then made possible using a map-reduce approach: \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mfirst using each community summary to answer the query independently and in parallel, then summarizing all \u001b[0m\u001b[1;31m    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mrelevant partial answers into a final global answer.\u001b[0m\u001b[1;31m                                                           \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m                                                                                                               \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mQuestion: What are the main advantages of using the Graph RAG approach for query-focused summarization compared\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mto traditional RAG methods?\u001b[0m\u001b[1;31m                                                                                    \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31mAnswer:\u001b[0m\u001b[1;31m                                                                                                        \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m                                                                                                               \u001b[0m\u001b[1;31m \u001b[0m\u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╭─────────────────────────────────────────────────</span> RAG Response <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">──────────────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ The main advantages of using the Graph RAG approach for query-focused summarization compared to traditional RAG │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ methods include:                                                                                                │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ 1. **Improved Comprehensiveness and Diversity**: Graph RAG shows substantial improvements over a naïve RAG      │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ baseline in terms of the comprehensiveness and diversity of answers. This is particularly beneficial for global │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ sensemaking questions over large datasets.                                                                      │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ 2. **Scalability**: Graph RAG provides scalability advantages, achieving efficient summarization with           │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ significantly fewer context tokens required. For instance, it requires 26-33% fewer tokens for low-level        │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ community summaries and over 97% fewer tokens for root-level summaries compared to source text summarization.   │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ 3. **Efficiency in Iterative Question Answering**: Root-level Graph RAG offers a highly efficient method for    │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ iterative question answering, which is crucial for sensemaking activities, with only a modest drop in           │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ performance compared to other global methods.                                                                   │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ 4. **Global Query Handling**: It supports handling global queries effectively, as it combines knowledge graph   │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ generation, retrieval-augmented generation, and query-focused summarization, making it suitable for sensemaking │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ over entire text corpora.                                                                                       │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ 5. **Hierarchical Indexing and Summarization**: The use of a hierarchical index and summarization allows for    │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ efficient processing and summarizing of community summaries into a final global answer, facilitating a          │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ comprehensive coverage of the underlying graph index and input documents.                                       │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│                                                                                                                 │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ 6. **Reduced Token Cost**: For situations requiring many global queries over the same dataset, Graph RAG        │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│ achieves competitive performance to other global methods at a fraction of the token cost.                       │</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;32m╭─\u001b[0m\u001b[1;32m────────────────────────────────────────────────\u001b[0m RAG Response \u001b[1;32m─────────────────────────────────────────────────\u001b[0m\u001b[1;32m─╮\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mThe main advantages of using the Graph RAG approach for query-focused summarization compared to traditional RAG\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mmethods include:\u001b[0m\u001b[1;32m                                                                                               \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m                                                                                                               \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m1. **Improved Comprehensiveness and Diversity**: Graph RAG shows substantial improvements over a naïve RAG \u001b[0m\u001b[1;32m    \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mbaseline in terms of the comprehensiveness and diversity of answers. This is particularly beneficial for global\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32msensemaking questions over large datasets.\u001b[0m\u001b[1;32m                                                                     \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m                                                                                                               \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m2. **Scalability**: Graph RAG provides scalability advantages, achieving efficient summarization with \u001b[0m\u001b[1;32m         \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32msignificantly fewer context tokens required. For instance, it requires 26-33% fewer tokens for low-level \u001b[0m\u001b[1;32m      \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mcommunity summaries and over 97% fewer tokens for root-level summaries compared to source text summarization.\u001b[0m\u001b[1;32m  \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m                                                                                                               \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m3. **Efficiency in Iterative Question Answering**: Root-level Graph RAG offers a highly efficient method for \u001b[0m\u001b[1;32m  \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32miterative question answering, which is crucial for sensemaking activities, with only a modest drop in \u001b[0m\u001b[1;32m         \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mperformance compared to other global methods.\u001b[0m\u001b[1;32m                                                                  \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m                                                                                                               \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m4. **Global Query Handling**: It supports handling global queries effectively, as it combines knowledge graph \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mgeneration, retrieval-augmented generation, and query-focused summarization, making it suitable for sensemaking\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mover entire text corpora.\u001b[0m\u001b[1;32m                                                                                      \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m                                                                                                               \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m5. **Hierarchical Indexing and Summarization**: The use of a hierarchical index and summarization allows for \u001b[0m\u001b[1;32m  \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mefficient processing and summarizing of community summaries into a final global answer, facilitating a \u001b[0m\u001b[1;32m        \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32mcomprehensive coverage of the underlying graph index and input documents.\u001b[0m\u001b[1;32m                                      \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m                                                                                                               \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m6. **Reduced Token Cost**: For situations requiring many global queries over the same dataset, Graph RAG \u001b[0m\u001b[1;32m      \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32machieves competitive performance to other global methods at a fraction of the token cost.\u001b[0m\u001b[1;32m                      \u001b[0m\u001b[1;32m \u001b[0m\u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from azure.search.documents.models import VectorizableTextQuery\n",
    "\n",
    "\n",
    "def generate_chat_response(prompt: str, system_message: str = None):\n",
    "    \"\"\"\n",
    "    Generates a single-turn chat response using Azure OpenAI Chat.\n",
    "    If you need multi-turn conversation or follow-up queries, you'll have to\n",
    "    maintain the messages list externally.\n",
    "    \"\"\"\n",
    "    messages = []\n",
    "    if system_message:\n",
    "        messages.append({\"role\": \"system\", \"content\": system_message})\n",
    "    messages.append({\"role\": \"user\", \"content\": prompt})\n",
    "\n",
    "    completion = openai_client.chat.completions.create(\n",
    "        model=AZURE_OPENAI_CHAT_MODEL, messages=messages, temperature=0.7\n",
    "    )\n",
    "    return completion.choices[0].message.content\n",
    "\n",
    "\n",
    "user_query = \"What are the main advantages of using the Graph RAG approach for query-focused summarization compared to traditional RAG methods?\"\n",
    "user_embed = embed_text(user_query)\n",
    "\n",
    "vector_query = VectorizableTextQuery(\n",
    "    text=user_query,  # passing in text for a hybrid search\n",
    "    k_nearest_neighbors=5,\n",
    "    fields=\"content_vector\",\n",
    ")\n",
    "\n",
    "search_results = search_client.search(\n",
    "    search_text=user_query, vector_queries=[vector_query], select=[\"content\"], top=10\n",
    ")\n",
    "\n",
    "retrieved_chunks = []\n",
    "for result in search_results:\n",
    "    snippet = result[\"content\"]\n",
    "    retrieved_chunks.append(snippet)\n",
    "\n",
    "context_str = \"\\n---\\n\".join(retrieved_chunks)\n",
    "rag_prompt = f\"\"\"\n",
    "You are an AI assistant helping answering questions about Microsoft GraphRAG.\n",
    "Use ONLY the text below to answer the user's question.\n",
    "If the answer isn't in the text, say you don't know.\n",
    "\n",
    "Context:\n",
    "{context_str}\n",
    "\n",
    "Question: {user_query}\n",
    "Answer:\n",
    "\"\"\"\n",
    "\n",
    "final_answer = generate_chat_response(rag_prompt)\n",
    "\n",
    "console.print(Panel(rag_prompt, title=\"RAG Prompt\", style=\"bold red\"))\n",
    "console.print(Panel(final_answer, title=\"RAG Response\", style=\"bold green\"))"
   ]
  }
 ],
 "metadata": {
  "accelerator": "GPU",
  "colab": {
   "gpuType": "T4",
   "provenance": []
  },
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}

```
</content>
</file_27>

<file_28>
<path>examples/rag_haystack.ipynb</path>
<content>
```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<a href=\"https://colab.research.google.com/github/DS4SD/docling/blob/main/docs/examples/rag_haystack.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# RAG with Haystack"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "| Step | Tech | Execution | \n",
    "| --- | --- | --- |\n",
    "| Embedding | Hugging Face / Sentence Transformers | 💻 Local |\n",
    "| Vector store | Milvus | 💻 Local |\n",
    "| Gen AI | Hugging Face Inference API | 🌐 Remote | "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Overview"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This example leverages the\n",
    "[Haystack Docling extension](../../integrations/haystack/), along with\n",
    "Milvus-based document store and retriever instances, as well as sentence-transformers\n",
    "embeddings.\n",
    "\n",
    "The presented `DoclingConverter` component enables you to:\n",
    "- use various document types in your LLM applications with ease and speed, and\n",
    "- leverage Docling's rich format for advanced, document-native grounding.\n",
    "\n",
    "`DoclingConverter` supports two different export modes:\n",
    "- `ExportType.MARKDOWN`: if you want to capture each input document as a separate\n",
    "  Haystack document, or\n",
    "- `ExportType.DOC_CHUNKS` (default): if you want to have each input document chunked and\n",
    "  to then capture each individual chunk as a separate Haystack document downstream.\n",
    "\n",
    "The example allows to explore both modes via parameter `EXPORT_TYPE`; depending on the\n",
    "value set, the ingestion and RAG pipelines are then set up accordingly."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Setup"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "- 👉 For best conversion speed, use GPU acceleration whenever available; e.g. if running on Colab, use GPU-enabled runtime.\n",
    "- Notebook uses HuggingFace's Inference API; for increased LLM quota, token can be provided via env var `HF_TOKEN`.\n",
    "- Requirements can be installed as shown below (`--no-warn-conflicts` meant for Colab's pre-populated Python env; feel free to remove for stricter usage):"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    }
   ],
   "source": [
    "%pip install -q --progress-bar off --no-warn-conflicts docling-haystack haystack-ai docling pymilvus milvus-haystack sentence-transformers python-dotenv"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from pathlib import Path\n",
    "from tempfile import mkdtemp\n",
    "\n",
    "from docling_haystack.converter import ExportType\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "\n",
    "def _get_env_from_colab_or_os(key):\n",
    "    try:\n",
    "        from google.colab import userdata\n",
    "\n",
    "        try:\n",
    "            return userdata.get(key)\n",
    "        except userdata.SecretNotFoundError:\n",
    "            pass\n",
    "    except ImportError:\n",
    "        pass\n",
    "    return os.getenv(key)\n",
    "\n",
    "\n",
    "load_dotenv()\n",
    "HF_TOKEN = _get_env_from_colab_or_os(\"HF_TOKEN\")\n",
    "PATHS = [\"https://arxiv.org/pdf/2408.09869\"]  # Docling Technical Report\n",
    "EMBED_MODEL_ID = \"sentence-transformers/all-MiniLM-L6-v2\"\n",
    "GENERATION_MODEL_ID = \"mistralai/Mixtral-8x7B-Instruct-v0.1\"\n",
    "EXPORT_TYPE = ExportType.DOC_CHUNKS\n",
    "QUESTION = \"Which are the main AI models in Docling?\"\n",
    "TOP_K = 3\n",
    "MILVUS_URI = str(Path(mkdtemp()) / \"docling.db\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Indexing pipeline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Token indices sequence length is longer than the specified maximum sequence length for this model (1041 > 512). Running this sequence through the model will result in indexing errors\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "80beca8762c34095a21467fb7f056059",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Batches:   0%|          | 0/2 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/plain": [
       "{'writer': {'documents_written': 54}}"
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "from docling_haystack.converter import DoclingConverter\n",
    "from haystack import Pipeline\n",
    "from haystack.components.embedders import (\n",
    "    SentenceTransformersDocumentEmbedder,\n",
    "    SentenceTransformersTextEmbedder,\n",
    ")\n",
    "from haystack.components.preprocessors import DocumentSplitter\n",
    "from haystack.components.writers import DocumentWriter\n",
    "from milvus_haystack import MilvusDocumentStore, MilvusEmbeddingRetriever\n",
    "\n",
    "from docling.chunking import HybridChunker\n",
    "\n",
    "document_store = MilvusDocumentStore(\n",
    "    connection_args={\"uri\": MILVUS_URI},\n",
    "    drop_old=True,\n",
    "    text_field=\"txt\",  # set for preventing conflict with same-name metadata field\n",
    ")\n",
    "\n",
    "idx_pipe = Pipeline()\n",
    "idx_pipe.add_component(\n",
    "    \"converter\",\n",
    "    DoclingConverter(\n",
    "        export_type=EXPORT_TYPE,\n",
    "        chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),\n",
    "    ),\n",
    ")\n",
    "idx_pipe.add_component(\n",
    "    \"embedder\",\n",
    "    SentenceTransformersDocumentEmbedder(model=EMBED_MODEL_ID),\n",
    ")\n",
    "idx_pipe.add_component(\"writer\", DocumentWriter(document_store=document_store))\n",
    "if EXPORT_TYPE == ExportType.DOC_CHUNKS:\n",
    "    idx_pipe.connect(\"converter\", \"embedder\")\n",
    "elif EXPORT_TYPE == ExportType.MARKDOWN:\n",
    "    idx_pipe.add_component(\n",
    "        \"splitter\",\n",
    "        DocumentSplitter(split_by=\"sentence\", split_length=1),\n",
    "    )\n",
    "    idx_pipe.connect(\"converter.documents\", \"splitter.documents\")\n",
    "    idx_pipe.connect(\"splitter.documents\", \"embedder.documents\")\n",
    "else:\n",
    "    raise ValueError(f\"Unexpected export type: {EXPORT_TYPE}\")\n",
    "idx_pipe.connect(\"embedder\", \"writer\")\n",
    "idx_pipe.run({\"converter\": {\"paths\": PATHS}})"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## RAG pipeline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "d753748e2b624896ad2caf5e8368b041",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Batches:   0%|          | 0/1 [00:00<?, ?it/s]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/pva/work/github.com/DS4SD/docling/.venv/lib/python3.12/site-packages/huggingface_hub/inference/_client.py:2232: FutureWarning: `stop_sequences` is a deprecated argument for `text_generation` task and will be removed in version '0.28.0'. Use `stop` instead.\n",
      "  warnings.warn(\n"
     ]
    }
   ],
   "source": [
    "from haystack.components.builders import AnswerBuilder\n",
    "from haystack.components.builders.prompt_builder import PromptBuilder\n",
    "from haystack.components.generators import HuggingFaceAPIGenerator\n",
    "from haystack.utils import Secret\n",
    "\n",
    "prompt_template = \"\"\"\n",
    "    Given these documents, answer the question.\n",
    "    Documents:\n",
    "    {% for doc in documents %}\n",
    "        {{ doc.content }}\n",
    "    {% endfor %}\n",
    "    Question: {{query}}\n",
    "    Answer:\n",
    "    \"\"\"\n",
    "\n",
    "rag_pipe = Pipeline()\n",
    "rag_pipe.add_component(\n",
    "    \"embedder\",\n",
    "    SentenceTransformersTextEmbedder(model=EMBED_MODEL_ID),\n",
    ")\n",
    "rag_pipe.add_component(\n",
    "    \"retriever\",\n",
    "    MilvusEmbeddingRetriever(document_store=document_store, top_k=TOP_K),\n",
    ")\n",
    "rag_pipe.add_component(\"prompt_builder\", PromptBuilder(template=prompt_template))\n",
    "rag_pipe.add_component(\n",
    "    \"llm\",\n",
    "    HuggingFaceAPIGenerator(\n",
    "        api_type=\"serverless_inference_api\",\n",
    "        api_params={\"model\": GENERATION_MODEL_ID},\n",
    "        token=Secret.from_token(HF_TOKEN) if HF_TOKEN else None,\n",
    "    ),\n",
    ")\n",
    "rag_pipe.add_component(\"answer_builder\", AnswerBuilder())\n",
    "rag_pipe.connect(\"embedder.embedding\", \"retriever\")\n",
    "rag_pipe.connect(\"retriever\", \"prompt_builder.documents\")\n",
    "rag_pipe.connect(\"prompt_builder\", \"llm\")\n",
    "rag_pipe.connect(\"llm.replies\", \"answer_builder.replies\")\n",
    "rag_pipe.connect(\"llm.meta\", \"answer_builder.meta\")\n",
    "rag_pipe.connect(\"retriever\", \"answer_builder.documents\")\n",
    "rag_res = rag_pipe.run(\n",
    "    {\n",
    "        \"embedder\": {\"text\": QUESTION},\n",
    "        \"prompt_builder\": {\"query\": QUESTION},\n",
    "        \"answer_builder\": {\"query\": QUESTION},\n",
    "    }\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Below we print out the RAG results. If you have used `ExportType.DOC_CHUNKS`, notice how\n",
    "the sources contain document-level grounding (e.g. page number or bounding box\n",
    "information):"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Question:\n",
      "Which are the main AI models in Docling?\n",
      "\n",
      "Answer:\n",
      "The main AI models in Docling are a layout analysis model and TableFormer. The layout analysis model is an accurate object-detector for page elements, while TableFormer is a state-of-the-art table structure recognition model. These models are provided with pre-trained weights and a separate package for the inference code as docling-ibm-models. They are also used in the open-access deepsearch-experience, a cloud-native service for knowledge exploration tasks. Additionally, Docling plans to extend its model library with a figure-classifier model, an equation-recognition model, a code-recognition model, and more in the future.\n",
      "\n",
      "Sources:\n",
      "- text: 'As part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page elements [13]. The second model is TableFormer [12, 9], a state-of-the-art table structure recognition model. We provide the pre-trained weights (hosted on huggingface) and a separate package for the inference code as docling-ibm-models . Both models are also powering the open-access deepsearch-experience, our cloud-native service for knowledge exploration tasks.'\n",
      "  file: 2408.09869v5.pdf\n",
      "  section: 3.2 AI models\n",
      "  page: 3, bounding box: [107, 406, 504, 330]\n",
      "- text: 'Docling implements a linear pipeline of operations, which execute sequentially on each given document (see Fig. 1). Each document is first parsed by a PDF backend, which retrieves the programmatic text tokens, consisting of string content and its coordinates on the page, and also renders a bitmap image of each page to support downstream operations. Then, the standard model pipeline applies a sequence of AI models independently on every page in the document to extract features and content, such as layout and table structures. Finally, the results from all pages are aggregated and passed through a post-processing stage, which augments metadata, detects the document language, infers reading-order and eventually assembles a typed document object which can be serialized to JSON or Markdown.'\n",
      "  file: 2408.09869v5.pdf\n",
      "  section: 3 Processing pipeline\n",
      "  page: 2, bounding box: [107, 273, 504, 176]\n",
      "- text: 'Docling is designed to allow easy extension of the model library and pipelines. In the future, we plan to extend Docling with several more models, such as a figure-classifier model, an equationrecognition model, a code-recognition model and more. This will help improve the quality of conversion for specific types of content, as well as augment extracted document metadata with additional information. Further investment into testing and optimizing GPU acceleration as well as improving the Docling-native PDF backend are on our roadmap, too.\\nWe encourage everyone to propose or implement additional features and models, and will gladly take your inputs and contributions under review . The codebase of Docling is open for use and contribution, under the MIT license agreement and in alignment with our contributing guidelines included in the Docling repository. If you use Docling in your projects, please consider citing this technical report.'\n",
      "  section: 6 Future work and contributions\n",
      "  page: 5, bounding box: [106, 323, 504, 258]\n"
     ]
    }
   ],
   "source": [
    "from docling.chunking import DocChunk\n",
    "\n",
    "print(f\"Question:\\n{QUESTION}\\n\")\n",
    "print(f\"Answer:\\n{rag_res['answer_builder']['answers'][0].data.strip()}\\n\")\n",
    "print(\"Sources:\")\n",
    "sources = rag_res[\"answer_builder\"][\"answers\"][0].documents\n",
    "for source in sources:\n",
    "    if EXPORT_TYPE == ExportType.DOC_CHUNKS:\n",
    "        doc_chunk = DocChunk.model_validate(source.meta[\"dl_meta\"])\n",
    "        print(f\"- text: {repr(doc_chunk.text)}\")\n",
    "        if doc_chunk.meta.origin:\n",
    "            print(f\"  file: {doc_chunk.meta.origin.filename}\")\n",
    "        if doc_chunk.meta.headings:\n",
    "            print(f\"  section: {' / '.join(doc_chunk.meta.headings)}\")\n",
    "        bbox = doc_chunk.meta.doc_items[0].prov[0].bbox\n",
    "        print(\n",
    "            f\"  page: {doc_chunk.meta.doc_items[0].prov[0].page_no}, \"\n",
    "            f\"bounding box: [{int(bbox.l)}, {int(bbox.t)}, {int(bbox.r)}, {int(bbox.b)}]\"\n",
    "        )\n",
    "    elif EXPORT_TYPE == ExportType.MARKDOWN:\n",
    "        print(repr(source.content))\n",
    "    else:\n",
    "        raise ValueError(f\"Unexpected export type: {EXPORT_TYPE}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

```
</content>
</file_28>

<file_29>
<path>examples/rag_langchain.ipynb</path>
<content>
```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<a href=\"https://colab.research.google.com/github/DS4SD/docling/blob/main/docs/examples/rag_langchain.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# RAG with LangChain"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "| Step | Tech | Execution | \n",
    "| --- | --- | --- |\n",
    "| Embedding | Hugging Face / Sentence Transformers | 💻 Local |\n",
    "| Vector store | Milvus | 💻 Local |\n",
    "| Gen AI | Hugging Face Inference API | 🌐 Remote | "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This example leverages the\n",
    "[LangChain Docling integration](../../integrations/langchain/), along with a Milvus\n",
    "vector store, as well as sentence-transformers embeddings.\n",
    "\n",
    "The presented `DoclingLoader` component enables you to:\n",
    "- use various document types in your LLM applications with ease and speed, and\n",
    "- leverage Docling's rich format for advanced, document-native grounding.\n",
    "\n",
    "`DoclingLoader` supports two different export modes:\n",
    "- `ExportType.MARKDOWN`: if you want to capture each input document as a separate\n",
    "  LangChain document, or\n",
    "- `ExportType.DOC_CHUNKS` (default): if you want to have each input document chunked and\n",
    "  to then capture each individual chunk as a separate LangChain document downstream.\n",
    "\n",
    "The example allows exploring both modes via parameter `EXPORT_TYPE`; depending on the\n",
    "value set, the example pipeline is then set up accordingly."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Setup"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "- 👉 For best conversion speed, use GPU acceleration whenever available; e.g. if running on Colab, use GPU-enabled runtime.\n",
    "- Notebook uses HuggingFace's Inference API; for increased LLM quota, token can be provided via env var `HF_TOKEN`.\n",
    "- Requirements can be installed as shown below (`--no-warn-conflicts` meant for Colab's pre-populated Python env; feel free to remove for stricter usage):"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    }
   ],
   "source": [
    "%pip install -q --progress-bar off --no-warn-conflicts langchain-docling langchain-core langchain-huggingface langchain_milvus langchain python-dotenv"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from pathlib import Path\n",
    "from tempfile import mkdtemp\n",
    "\n",
    "from dotenv import load_dotenv\n",
    "from langchain_core.prompts import PromptTemplate\n",
    "from langchain_docling.loader import ExportType\n",
    "\n",
    "\n",
    "def _get_env_from_colab_or_os(key):\n",
    "    try:\n",
    "        from google.colab import userdata\n",
    "\n",
    "        try:\n",
    "            return userdata.get(key)\n",
    "        except userdata.SecretNotFoundError:\n",
    "            pass\n",
    "    except ImportError:\n",
    "        pass\n",
    "    return os.getenv(key)\n",
    "\n",
    "\n",
    "load_dotenv()\n",
    "\n",
    "# https://github.com/huggingface/transformers/issues/5486:\n",
    "os.environ[\"TOKENIZERS_PARALLELISM\"] = \"false\"\n",
    "\n",
    "HF_TOKEN = _get_env_from_colab_or_os(\"HF_TOKEN\")\n",
    "FILE_PATH = [\"https://arxiv.org/pdf/2408.09869\"]  # Docling Technical Report\n",
    "EMBED_MODEL_ID = \"sentence-transformers/all-MiniLM-L6-v2\"\n",
    "GEN_MODEL_ID = \"mistralai/Mixtral-8x7B-Instruct-v0.1\"\n",
    "EXPORT_TYPE = ExportType.DOC_CHUNKS\n",
    "QUESTION = \"Which are the main AI models in Docling?\"\n",
    "PROMPT = PromptTemplate.from_template(\n",
    "    \"Context information is below.\\n---------------------\\n{context}\\n---------------------\\nGiven the context information and not prior knowledge, answer the query.\\nQuery: {input}\\nAnswer:\\n\",\n",
    ")\n",
    "TOP_K = 3\n",
    "MILVUS_URI = str(Path(mkdtemp()) / \"docling.db\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Document loading\n",
    "\n",
    "Now we can instantiate our loader and load documents."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Token indices sequence length is longer than the specified maximum sequence length for this model (1041 > 512). Running this sequence through the model will result in indexing errors\n"
     ]
    }
   ],
   "source": [
    "from langchain_docling import DoclingLoader\n",
    "\n",
    "from docling.chunking import HybridChunker\n",
    "\n",
    "loader = DoclingLoader(\n",
    "    file_path=FILE_PATH,\n",
    "    export_type=EXPORT_TYPE,\n",
    "    chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),\n",
    ")\n",
    "\n",
    "docs = loader.load()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "> Note: a message saying `\"Token indices sequence length is longer than the specified\n",
    "maximum sequence length...\"` can be ignored in this case — details\n",
    "[here](https://github.com/DS4SD/docling-core/issues/119#issuecomment-2577418826)."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Determining the splits:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "if EXPORT_TYPE == ExportType.DOC_CHUNKS:\n",
    "    splits = docs\n",
    "elif EXPORT_TYPE == ExportType.MARKDOWN:\n",
    "    from langchain_text_splitters import MarkdownHeaderTextSplitter\n",
    "\n",
    "    splitter = MarkdownHeaderTextSplitter(\n",
    "        headers_to_split_on=[\n",
    "            (\"#\", \"Header_1\"),\n",
    "            (\"##\", \"Header_2\"),\n",
    "            (\"###\", \"Header_3\"),\n",
    "        ],\n",
    "    )\n",
    "    splits = [split for doc in docs for split in splitter.split_text(doc.page_content)]\n",
    "else:\n",
    "    raise ValueError(f\"Unexpected export type: {EXPORT_TYPE}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Inspecting some sample splits:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "- d.page_content='arXiv:2408.09869v5  [cs.CL]  9 Dec 2024'\n",
      "- d.page_content='Docling Technical Report\\nVersion 1.0\\nChristoph Auer Maksym Lysak Ahmed Nassar Michele Dolfi Nikolaos Livathinos Panos Vagenas Cesar Berrospi Ramis Matteo Omenetti Fabian Lindlbauer Kasper Dinkla Lokesh Mishra Yusik Kim Shubham Gupta Rafael Teixeira de Lima Valery Weber Lucas Morin Ingmar Meijer Viktor Kuropiatnyk Peter W. J. Staar\\nAI4K Group, IBM Research R¨uschlikon, Switzerland'\n",
      "- d.page_content='Abstract\\nThis technical report introduces Docling , an easy to use, self-contained, MITlicensed open-source package for PDF document conversion. It is powered by state-of-the-art specialized AI models for layout analysis (DocLayNet) and table structure recognition (TableFormer), and runs efficiently on commodity hardware in a small resource budget. The code interface allows for easy extensibility and addition of new features and models.'\n",
      "...\n"
     ]
    }
   ],
   "source": [
    "for d in splits[:3]:\n",
    "    print(f\"- {d.page_content=}\")\n",
    "print(\"...\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Ingestion"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "from pathlib import Path\n",
    "from tempfile import mkdtemp\n",
    "\n",
    "from langchain_huggingface.embeddings import HuggingFaceEmbeddings\n",
    "from langchain_milvus import Milvus\n",
    "\n",
    "embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)\n",
    "\n",
    "\n",
    "milvus_uri = str(Path(mkdtemp()) / \"docling.db\")  # or set as needed\n",
    "vectorstore = Milvus.from_documents(\n",
    "    documents=splits,\n",
    "    embedding=embedding,\n",
    "    collection_name=\"docling_demo\",\n",
    "    connection_args={\"uri\": milvus_uri},\n",
    "    index_params={\"index_type\": \"FLAT\"},\n",
    "    drop_old=True,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## RAG"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Note: Environment variable`HF_TOKEN` is set and is the current active token independently from the token you've just configured.\n"
     ]
    }
   ],
   "source": [
    "from langchain.chains import create_retrieval_chain\n",
    "from langchain.chains.combine_documents import create_stuff_documents_chain\n",
    "from langchain_huggingface import HuggingFaceEndpoint\n",
    "\n",
    "retriever = vectorstore.as_retriever(search_kwargs={\"k\": TOP_K})\n",
    "llm = HuggingFaceEndpoint(\n",
    "    repo_id=GEN_MODEL_ID,\n",
    "    huggingfacehub_api_token=HF_TOKEN,\n",
    ")\n",
    "\n",
    "\n",
    "def clip_text(text, threshold=100):\n",
    "    return f\"{text[:threshold]}...\" if len(text) > threshold else text"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Question:\n",
      "Which are the main AI models in Docling?\n",
      "\n",
      "Answer:\n",
      "Docling initially releases two AI models, a layout analysis model and TableFormer. The layout analysis model is an accurate object-detector for page elements, and TableFormer is a state-of-the-art tab...\n",
      "\n",
      "Source 1:\n",
      "  text: \"3.2 AI models\\nAs part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page elements [13]. The second model is TableFormer [12, 9], a state-of-the-art table structure re...\"\n",
      "  dl_meta: {'schema_name': 'docling_core.transforms.chunker.DocMeta', 'version': '1.0.0', 'doc_items': [{'self_ref': '#/texts/50', 'parent': {'$ref': '#/body'}, 'children': [], 'label': 'text', 'prov': [{'page_no': 3, 'bbox': {'l': 108.0, 't': 405.1419982910156, 'r': 504.00299072265625, 'b': 330.7799987792969, 'coord_origin': 'BOTTOMLEFT'}, 'charspan': [0, 608]}]}], 'headings': ['3.2 AI models'], 'origin': {'mimetype': 'application/pdf', 'binary_hash': 11465328351749295394, 'filename': '2408.09869v5.pdf'}}\n",
      "  source: https://arxiv.org/pdf/2408.09869\n",
      "\n",
      "Source 2:\n",
      "  text: \"3 Processing pipeline\\nDocling implements a linear pipeline of operations, which execute sequentially on each given document (see Fig. 1). Each document is first parsed by a PDF backend, which retrieves the programmatic text tokens, consisting of string content and its coordinates on the page, and also renders a bitmap image of each page to support ...\"\n",
      "  dl_meta: {'schema_name': 'docling_core.transforms.chunker.DocMeta', 'version': '1.0.0', 'doc_items': [{'self_ref': '#/texts/26', 'parent': {'$ref': '#/body'}, 'children': [], 'label': 'text', 'prov': [{'page_no': 2, 'bbox': {'l': 108.0, 't': 273.01800537109375, 'r': 504.00299072265625, 'b': 176.83799743652344, 'coord_origin': 'BOTTOMLEFT'}, 'charspan': [0, 796]}]}], 'headings': ['3 Processing pipeline'], 'origin': {'mimetype': 'application/pdf', 'binary_hash': 11465328351749295394, 'filename': '2408.09869v5.pdf'}}\n",
      "  source: https://arxiv.org/pdf/2408.09869\n",
      "\n",
      "Source 3:\n",
      "  text: \"6 Future work and contributions\\nDocling is designed to allow easy extension of the model library and pipelines. In the future, we plan to extend Docling with several more models, such as a figure-classifier model, an equationrecognition model, a code-recognition model and more. This will help improve the quality of conversion for specific types of ...\"\n",
      "  dl_meta: {'schema_name': 'docling_core.transforms.chunker.DocMeta', 'version': '1.0.0', 'doc_items': [{'self_ref': '#/texts/76', 'parent': {'$ref': '#/body'}, 'children': [], 'label': 'text', 'prov': [{'page_no': 5, 'bbox': {'l': 108.0, 't': 322.468994140625, 'r': 504.00299072265625, 'b': 259.0169982910156, 'coord_origin': 'BOTTOMLEFT'}, 'charspan': [0, 543]}]}, {'self_ref': '#/texts/77', 'parent': {'$ref': '#/body'}, 'children': [], 'label': 'text', 'prov': [{'page_no': 5, 'bbox': {'l': 108.0, 't': 251.6540069580078, 'r': 504.00299072265625, 'b': 198.99200439453125, 'coord_origin': 'BOTTOMLEFT'}, 'charspan': [0, 402]}]}], 'headings': ['6 Future work and contributions'], 'origin': {'mimetype': 'application/pdf', 'binary_hash': 11465328351749295394, 'filename': '2408.09869v5.pdf'}}\n",
      "  source: https://arxiv.org/pdf/2408.09869\n"
     ]
    }
   ],
   "source": [
    "question_answer_chain = create_stuff_documents_chain(llm, PROMPT)\n",
    "rag_chain = create_retrieval_chain(retriever, question_answer_chain)\n",
    "resp_dict = rag_chain.invoke({\"input\": QUESTION})\n",
    "\n",
    "clipped_answer = clip_text(resp_dict[\"answer\"], threshold=200)\n",
    "print(f\"Question:\\n{resp_dict['input']}\\n\\nAnswer:\\n{clipped_answer}\")\n",
    "for i, doc in enumerate(resp_dict[\"context\"]):\n",
    "    print()\n",
    "    print(f\"Source {i+1}:\")\n",
    "    print(f\"  text: {json.dumps(clip_text(doc.page_content, threshold=350))}\")\n",
    "    for key in doc.metadata:\n",
    "        if key != \"pk\":\n",
    "            val = doc.metadata.get(key)\n",
    "            clipped_val = clip_text(val) if isinstance(val, str) else val\n",
    "            print(f\"  {key}: {clipped_val}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

```
</content>
</file_29>

<file_30>
<path>examples/rag_llamaindex.ipynb</path>
<content>
```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<a href=\"https://colab.research.google.com/github/DS4SD/docling/blob/main/docs/examples/rag_llamaindex.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# RAG with LlamaIndex"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "| Step | Tech | Execution | \n",
    "| --- | --- | --- |\n",
    "| Embedding | Hugging Face / Sentence Transformers | 💻 Local |\n",
    "| Vector store | Milvus | 💻 Local |\n",
    "| Gen AI | Hugging Face Inference API | 🌐 Remote | "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Overview"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This example leverages the official [LlamaIndex Docling extension](../../integrations/llamaindex/).\n",
    "\n",
    "Presented extensions `DoclingReader` and `DoclingNodeParser` enable you to:\n",
    "- use various document types in your LLM applications with ease and speed, and\n",
    "- leverage Docling's rich format for advanced, document-native grounding."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Setup"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "- 👉 For best conversion speed, use GPU acceleration whenever available; e.g. if running on Colab, use GPU-enabled runtime.\n",
    "- Notebook uses HuggingFace's Inference API; for increased LLM quota, token can be provided via env var `HF_TOKEN`.\n",
    "- Requirements can be installed as shown below (`--no-warn-conflicts` meant for Colab's pre-populated Python env; feel free to remove for stricter usage):"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    }
   ],
   "source": [
    "%pip install -q --progress-bar off --no-warn-conflicts llama-index-core llama-index-readers-docling llama-index-node-parser-docling llama-index-embeddings-huggingface llama-index-llms-huggingface-api llama-index-vector-stores-milvus llama-index-readers-file python-dotenv"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from pathlib import Path\n",
    "from tempfile import mkdtemp\n",
    "from warnings import filterwarnings\n",
    "\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "\n",
    "def _get_env_from_colab_or_os(key):\n",
    "    try:\n",
    "        from google.colab import userdata\n",
    "\n",
    "        try:\n",
    "            return userdata.get(key)\n",
    "        except userdata.SecretNotFoundError:\n",
    "            pass\n",
    "    except ImportError:\n",
    "        pass\n",
    "    return os.getenv(key)\n",
    "\n",
    "\n",
    "load_dotenv()\n",
    "\n",
    "filterwarnings(action=\"ignore\", category=UserWarning, module=\"pydantic\")\n",
    "filterwarnings(action=\"ignore\", category=FutureWarning, module=\"easyocr\")\n",
    "# https://github.com/huggingface/transformers/issues/5486:\n",
    "os.environ[\"TOKENIZERS_PARALLELISM\"] = \"false\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can now define the main parameters:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "from llama_index.embeddings.huggingface import HuggingFaceEmbedding\n",
    "from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI\n",
    "\n",
    "EMBED_MODEL = HuggingFaceEmbedding(model_name=\"BAAI/bge-small-en-v1.5\")\n",
    "MILVUS_URI = str(Path(mkdtemp()) / \"docling.db\")\n",
    "GEN_MODEL = HuggingFaceInferenceAPI(\n",
    "    token=_get_env_from_colab_or_os(\"HF_TOKEN\"),\n",
    "    model_name=\"mistralai/Mixtral-8x7B-Instruct-v0.1\",\n",
    ")\n",
    "SOURCE = \"https://arxiv.org/pdf/2408.09869\"  # Docling Technical Report\n",
    "QUERY = \"Which are the main AI models in Docling?\"\n",
    "\n",
    "embed_dim = len(EMBED_MODEL.get_text_embedding(\"hi\"))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Using Markdown export"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "To create a simple RAG pipeline, we can:\n",
    "- define a `DoclingReader`, which by default exports to Markdown, and\n",
    "- use a standard node parser for these Markdown-based docs, e.g. a `MarkdownNodeParser`"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Q: Which are the main AI models in Docling?\n",
      "A: The main AI models in Docling are a layout analysis model, which is an accurate object-detector for page elements, and TableFormer, a state-of-the-art table structure recognition model.\n",
      "\n",
      "Sources:\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "[('3.2 AI models\\n\\nAs part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page elements [13]. The second model is TableFormer [12, 9], a state-of-the-art table structure recognition model. We provide the pre-trained weights (hosted on huggingface) and a separate package for the inference code as docling-ibm-models . Both models are also powering the open-access deepsearch-experience, our cloud-native service for knowledge exploration tasks.',\n",
       "  {'Header_2': '3.2 AI models'}),\n",
       " (\"5 Applications\\n\\nThanks to the high-quality, richly structured document conversion achieved by Docling, its output qualifies for numerous downstream applications. For example, Docling can provide a base for detailed enterprise document search, passage retrieval or classification use-cases, or support knowledge extraction pipelines, allowing specific treatment of different structures in the document, such as tables, figures, section structure or references. For popular generative AI application patterns, such as retrieval-augmented generation (RAG), we provide quackling , an open-source package which capitalizes on Docling's feature-rich document output to enable document-native optimized vector embedding and chunking. It plugs in seamlessly with LLM frameworks such as LlamaIndex [8]. Since Docling is fast, stable and cheap to run, it also makes for an excellent choice to build document-derived datasets. With its powerful table structure recognition, it provides significant benefit to automated knowledge-base construction [11, 10]. Docling is also integrated within the open IBM data prep kit [6], which implements scalable data transforms to build large-scale multi-modal training datasets.\",\n",
       "  {'Header_2': '5 Applications'})]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from llama_index.core import StorageContext, VectorStoreIndex\n",
    "from llama_index.core.node_parser import MarkdownNodeParser\n",
    "from llama_index.readers.docling import DoclingReader\n",
    "from llama_index.vector_stores.milvus import MilvusVectorStore\n",
    "\n",
    "reader = DoclingReader()\n",
    "node_parser = MarkdownNodeParser()\n",
    "\n",
    "vector_store = MilvusVectorStore(\n",
    "    uri=str(Path(mkdtemp()) / \"docling.db\"),  # or set as needed\n",
    "    dim=embed_dim,\n",
    "    overwrite=True,\n",
    ")\n",
    "index = VectorStoreIndex.from_documents(\n",
    "    documents=reader.load_data(SOURCE),\n",
    "    transformations=[node_parser],\n",
    "    storage_context=StorageContext.from_defaults(vector_store=vector_store),\n",
    "    embed_model=EMBED_MODEL,\n",
    ")\n",
    "result = index.as_query_engine(llm=GEN_MODEL).query(QUERY)\n",
    "print(f\"Q: {QUERY}\\nA: {result.response.strip()}\\n\\nSources:\")\n",
    "display([(n.text, n.metadata) for n in result.source_nodes])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Using Docling format"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "To leverage Docling's rich native format, we:\n",
    "- create a `DoclingReader` with JSON export type, and\n",
    "- employ a `DoclingNodeParser` in order to appropriately parse that Docling format.\n",
    "\n",
    "Notice how the sources now also contain document-level grounding (e.g. page number or bounding box information):"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Q: Which are the main AI models in Docling?\n",
      "A: The main AI models in Docling are a layout analysis model and TableFormer. The layout analysis model is an accurate object-detector for page elements, and TableFormer is a state-of-the-art table structure recognition model.\n",
      "\n",
      "Sources:\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "[('As part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page elements [13]. The second model is TableFormer [12, 9], a state-of-the-art table structure recognition model. We provide the pre-trained weights (hosted on huggingface) and a separate package for the inference code as docling-ibm-models . Both models are also powering the open-access deepsearch-experience, our cloud-native service for knowledge exploration tasks.',\n",
       "  {'schema_name': 'docling_core.transforms.chunker.DocMeta',\n",
       "   'version': '1.0.0',\n",
       "   'doc_items': [{'self_ref': '#/texts/34',\n",
       "     'parent': {'$ref': '#/body'},\n",
       "     'children': [],\n",
       "     'label': 'text',\n",
       "     'prov': [{'page_no': 3,\n",
       "       'bbox': {'l': 107.07593536376953,\n",
       "        't': 406.1695251464844,\n",
       "        'r': 504.1148681640625,\n",
       "        'b': 330.2677307128906,\n",
       "        'coord_origin': 'BOTTOMLEFT'},\n",
       "       'charspan': [0, 608]}]}],\n",
       "   'headings': ['3.2 AI models'],\n",
       "   'origin': {'mimetype': 'application/pdf',\n",
       "    'binary_hash': 14981478401387673002,\n",
       "    'filename': '2408.09869v3.pdf'}}),\n",
       " ('With Docling , we open-source a very capable and efficient document conversion tool which builds on the powerful, specialized AI models and datasets for layout analysis and table structure recognition we developed and presented in the recent past [12, 13, 9]. Docling is designed as a simple, self-contained python library with permissive license, running entirely locally on commodity hardware. Its code architecture allows for easy extensibility and addition of new features and models.',\n",
       "  {'schema_name': 'docling_core.transforms.chunker.DocMeta',\n",
       "   'version': '1.0.0',\n",
       "   'doc_items': [{'self_ref': '#/texts/9',\n",
       "     'parent': {'$ref': '#/body'},\n",
       "     'children': [],\n",
       "     'label': 'text',\n",
       "     'prov': [{'page_no': 1,\n",
       "       'bbox': {'l': 107.0031967163086,\n",
       "        't': 136.7283935546875,\n",
       "        'r': 504.04998779296875,\n",
       "        'b': 83.30133056640625,\n",
       "        'coord_origin': 'BOTTOMLEFT'},\n",
       "       'charspan': [0, 488]}]}],\n",
       "   'headings': ['1 Introduction'],\n",
       "   'origin': {'mimetype': 'application/pdf',\n",
       "    'binary_hash': 14981478401387673002,\n",
       "    'filename': '2408.09869v3.pdf'}})]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from llama_index.node_parser.docling import DoclingNodeParser\n",
    "\n",
    "reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)\n",
    "node_parser = DoclingNodeParser()\n",
    "\n",
    "vector_store = MilvusVectorStore(\n",
    "    uri=str(Path(mkdtemp()) / \"docling.db\"),  # or set as needed\n",
    "    dim=embed_dim,\n",
    "    overwrite=True,\n",
    ")\n",
    "index = VectorStoreIndex.from_documents(\n",
    "    documents=reader.load_data(SOURCE),\n",
    "    transformations=[node_parser],\n",
    "    storage_context=StorageContext.from_defaults(vector_store=vector_store),\n",
    "    embed_model=EMBED_MODEL,\n",
    ")\n",
    "result = index.as_query_engine(llm=GEN_MODEL).query(QUERY)\n",
    "print(f\"Q: {QUERY}\\nA: {result.response.strip()}\\n\\nSources:\")\n",
    "display([(n.text, n.metadata) for n in result.source_nodes])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## With Simple Directory Reader"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "To demonstrate this usage pattern, we first set up a test document directory."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pathlib import Path\n",
    "from tempfile import mkdtemp\n",
    "\n",
    "import requests\n",
    "\n",
    "tmp_dir_path = Path(mkdtemp())\n",
    "r = requests.get(SOURCE)\n",
    "with open(tmp_dir_path / f\"{Path(SOURCE).name}.pdf\", \"wb\") as out_file:\n",
    "    out_file.write(r.content)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Using the `reader` and `node_parser` definitions from any of the above variants, usage with `SimpleDirectoryReader` then looks as follows:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Loading files: 100%|██████████| 1/1 [00:11<00:00, 11.27s/file]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Q: Which are the main AI models in Docling?\n",
      "A: 1. A layout analysis model, an accurate object-detector for page elements. 2. TableFormer, a state-of-the-art table structure recognition model.\n",
      "\n",
      "Sources:\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "[('As part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page elements [13]. The second model is TableFormer [12, 9], a state-of-the-art table structure recognition model. We provide the pre-trained weights (hosted on huggingface) and a separate package for the inference code as docling-ibm-models . Both models are also powering the open-access deepsearch-experience, our cloud-native service for knowledge exploration tasks.',\n",
       "  {'file_path': '/var/folders/76/4wwfs06x6835kcwj4186c0nc0000gn/T/tmp2ooyusg5/2408.09869.pdf',\n",
       "   'file_name': '2408.09869.pdf',\n",
       "   'file_type': 'application/pdf',\n",
       "   'file_size': 5566574,\n",
       "   'creation_date': '2024-10-28',\n",
       "   'last_modified_date': '2024-10-28',\n",
       "   'schema_name': 'docling_core.transforms.chunker.DocMeta',\n",
       "   'version': '1.0.0',\n",
       "   'doc_items': [{'self_ref': '#/texts/34',\n",
       "     'parent': {'$ref': '#/body'},\n",
       "     'children': [],\n",
       "     'label': 'text',\n",
       "     'prov': [{'page_no': 3,\n",
       "       'bbox': {'l': 107.07593536376953,\n",
       "        't': 406.1695251464844,\n",
       "        'r': 504.1148681640625,\n",
       "        'b': 330.2677307128906,\n",
       "        'coord_origin': 'BOTTOMLEFT'},\n",
       "       'charspan': [0, 608]}]}],\n",
       "   'headings': ['3.2 AI models'],\n",
       "   'origin': {'mimetype': 'application/pdf',\n",
       "    'binary_hash': 14981478401387673002,\n",
       "    'filename': '2408.09869.pdf'}}),\n",
       " ('With Docling , we open-source a very capable and efficient document conversion tool which builds on the powerful, specialized AI models and datasets for layout analysis and table structure recognition we developed and presented in the recent past [12, 13, 9]. Docling is designed as a simple, self-contained python library with permissive license, running entirely locally on commodity hardware. Its code architecture allows for easy extensibility and addition of new features and models.',\n",
       "  {'file_path': '/var/folders/76/4wwfs06x6835kcwj4186c0nc0000gn/T/tmp2ooyusg5/2408.09869.pdf',\n",
       "   'file_name': '2408.09869.pdf',\n",
       "   'file_type': 'application/pdf',\n",
       "   'file_size': 5566574,\n",
       "   'creation_date': '2024-10-28',\n",
       "   'last_modified_date': '2024-10-28',\n",
       "   'schema_name': 'docling_core.transforms.chunker.DocMeta',\n",
       "   'version': '1.0.0',\n",
       "   'doc_items': [{'self_ref': '#/texts/9',\n",
       "     'parent': {'$ref': '#/body'},\n",
       "     'children': [],\n",
       "     'label': 'text',\n",
       "     'prov': [{'page_no': 1,\n",
       "       'bbox': {'l': 107.0031967163086,\n",
       "        't': 136.7283935546875,\n",
       "        'r': 504.04998779296875,\n",
       "        'b': 83.30133056640625,\n",
       "        'coord_origin': 'BOTTOMLEFT'},\n",
       "       'charspan': [0, 488]}]}],\n",
       "   'headings': ['1 Introduction'],\n",
       "   'origin': {'mimetype': 'application/pdf',\n",
       "    'binary_hash': 14981478401387673002,\n",
       "    'filename': '2408.09869.pdf'}})]"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from llama_index.core import SimpleDirectoryReader\n",
    "\n",
    "dir_reader = SimpleDirectoryReader(\n",
    "    input_dir=tmp_dir_path,\n",
    "    file_extractor={\".pdf\": reader},\n",
    ")\n",
    "\n",
    "vector_store = MilvusVectorStore(\n",
    "    uri=str(Path(mkdtemp()) / \"docling.db\"),  # or set as needed\n",
    "    dim=embed_dim,\n",
    "    overwrite=True,\n",
    ")\n",
    "index = VectorStoreIndex.from_documents(\n",
    "    documents=dir_reader.load_data(SOURCE),\n",
    "    transformations=[node_parser],\n",
    "    storage_context=StorageContext.from_defaults(vector_store=vector_store),\n",
    "    embed_model=EMBED_MODEL,\n",
    ")\n",
    "result = index.as_query_engine(llm=GEN_MODEL).query(QUERY)\n",
    "print(f\"Q: {QUERY}\\nA: {result.response.strip()}\\n\\nSources:\")\n",
    "display([(n.text, n.metadata) for n in result.source_nodes])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

```
</content>
</file_30>

<file_31>
<path>examples/rag_weaviate.ipynb</path>
<content>
```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DS4SD/docling/blob/main/docs/examples/rag_weaviate.ipynb)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "Ag9kcX2B_atc"
   },
   "source": [
    "# RAG with Weaviate"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "\n",
    "| Step | Tech | Execution | \n",
    "| --- | --- | --- |\n",
    "| Embedding | Open AI | 🌐 Remote |\n",
    "| Vector store | Weavieate | 💻 Local |\n",
    "| Gen AI | Open AI | 🌐 Remote |\n",
    "\n",
    "## A recipe 🧑‍🍳 🐥 💚\n",
    "\n",
    "This is a code recipe that uses [Weaviate](https://weaviate.io/) to perform RAG over PDF documents parsed by [Docling](https://ds4sd.github.io/docling/).\n",
    "\n",
    "In this notebook, we accomplish the following:\n",
    "* Parse the top machine learning papers on [arXiv](https://arxiv.org/) using Docling\n",
    "* Perform hierarchical chunking of the documents using Docling\n",
    "* Generate text embeddings with OpenAI\n",
    "* Perform RAG using [Weaviate](https://weaviate.io/developers/weaviate/search/generative)\n",
    "\n",
    "To run this notebook, you'll need:\n",
    "* An [OpenAI API key](https://platform.openai.com/docs/quickstart)\n",
    "* Access to GPU/s\n",
    "\n",
    "Note: For best results, please use **GPU acceleration** to run this notebook. Here are two options for running this notebook:\n",
    "1. **Locally on a MacBook with an Apple Silicon chip.** Converting all documents in the notebook takes ~2 minutes on a MacBook M2 due to Docling's usage of MPS accelerators.\n",
    "2. **Run this notebook on Google Colab.** Converting all documents in the notebook takes ~8 mintutes on a Google Colab T4 GPU."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "4YgT7tpXCUl0"
   },
   "source": [
    "### Install Docling and Weaviate client\n",
    "\n",
    "Note: If Colab prompts you to restart the session after running the cell below, click \"restart\" and proceed with running the rest of the notebook."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "collapsed": true,
    "id": "u076oUSF_YUG"
   },
   "outputs": [],
   "source": [
    "%%capture\n",
    "%pip install docling~=\"2.7.0\"\n",
    "%pip install -U weaviate-client~=\"4.9.4\"\n",
    "%pip install rich\n",
    "%pip install torch\n",
    "\n",
    "import warnings\n",
    "\n",
    "warnings.filterwarnings(\"ignore\")\n",
    "\n",
    "import logging\n",
    "\n",
    "# Suppress Weaviate client logs\n",
    "logging.getLogger(\"weaviate\").setLevel(logging.ERROR)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "2q2F9RUmR8Wj"
   },
   "source": [
    "## 🐥 Part 1: Docling\n",
    "\n",
    "Part of what makes Docling so remarkable is the fact that it can run on commodity hardware. This means that this notebook can be run on a local machine with GPU acceleration. If you're using a MacBook with a silicon chip, Docling integrates seamlessly with Metal Performance Shaders (MPS). MPS provides out-of-the-box GPU acceleration for macOS, seamlessly integrating with PyTorch and TensorFlow, offering energy-efficient performance on Apple Silicon, and broad compatibility with all Metal-supported GPUs.\n",
    "\n",
    "The code below checks to see if a GPU is available, either via CUDA or MPS."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "MPS GPU is enabled.\n"
     ]
    }
   ],
   "source": [
    "import torch\n",
    "\n",
    "# Check if GPU or MPS is available\n",
    "if torch.cuda.is_available():\n",
    "    device = torch.device(\"cuda\")\n",
    "    print(f\"CUDA GPU is enabled: {torch.cuda.get_device_name(0)}\")\n",
    "elif torch.backends.mps.is_available():\n",
    "    device = torch.device(\"mps\")\n",
    "    print(\"MPS GPU is enabled.\")\n",
    "else:\n",
    "    raise EnvironmentError(\n",
    "        \"No GPU or MPS device found. Please check your environment and ensure GPU or MPS support is configured.\"\n",
    "    )"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "wHTsy4a8JFPl"
   },
   "source": [
    "Here, we've collected 10 influential machine learning papers published as PDFs on arXiv. Because Docling does not yet have title extraction for PDFs, we manually add the titles in a corresponding list.\n",
    "\n",
    "Note: Converting all 10 papers should take around 8 minutes with a T4 GPU."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "id": "Vy5SMPiGDMy-"
   },
   "outputs": [],
   "source": [
    "# Influential machine learning papers\n",
    "source_urls = [\n",
    "    \"https://arxiv.org/pdf/1706.03762\",\n",
    "    \"https://arxiv.org/pdf/1810.04805\",\n",
    "    \"https://arxiv.org/pdf/1406.2661\",\n",
    "    \"https://arxiv.org/pdf/1409.0473\",\n",
    "    \"https://arxiv.org/pdf/1412.6980\",\n",
    "    \"https://arxiv.org/pdf/1312.6114\",\n",
    "    \"https://arxiv.org/pdf/1312.5602\",\n",
    "    \"https://arxiv.org/pdf/1512.03385\",\n",
    "    \"https://arxiv.org/pdf/1409.3215\",\n",
    "    \"https://arxiv.org/pdf/1301.3781\",\n",
    "]\n",
    "\n",
    "# And their corresponding titles (because Docling doesn't have title extraction yet!)\n",
    "source_titles = [\n",
    "    \"Attention Is All You Need\",\n",
    "    \"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding\",\n",
    "    \"Generative Adversarial Nets\",\n",
    "    \"Neural Machine Translation by Jointly Learning to Align and Translate\",\n",
    "    \"Adam: A Method for Stochastic Optimization\",\n",
    "    \"Auto-Encoding Variational Bayes\",\n",
    "    \"Playing Atari with Deep Reinforcement Learning\",\n",
    "    \"Deep Residual Learning for Image Recognition\",\n",
    "    \"Sequence to Sequence Learning with Neural Networks\",\n",
    "    \"A Neural Probabilistic Language Model\",\n",
    "]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "5fi8wzHrCoLa"
   },
   "source": [
    "### Convert PDFs to Docling documents\n",
    "\n",
    "Here we use Docling's `.convert_all()` to parse a batch of PDFs. The result is a list of Docling documents that we can use for text extraction.\n",
    "\n",
    "Note: Please ignore the `ERR#` message."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 67,
     "referenced_widgets": [
      "6d049f786a2f4ad7857a6cf2d95b5ba2",
      "db2a7b9f549e4f0fb1ff3fce655d76a2",
      "630967a2db4c4714b4c15d1358a0fcae",
      "b3da9595ab7c4995a00e506e7b5202e3",
      "243ecaf36ee24cafbd1c33d148f2ca78",
      "5b7e22df1b464ca894126736e6f72207",
      "02f6af5993bb4a6a9dbca77952f675d2",
      "dea323b3de0e43118f338842c94ac065",
      "bd198d2c0c4c4933a6e6544908d0d846",
      "febd5c498e4f4f5dbde8dec3cd935502",
      "ab4f282c0d37451092c60e6566e8e945"
     ]
    },
    "id": "Sr44xGR1PNSc",
    "outputId": "b5cca9ee-d7c0-4c8f-c18a-0ac4787984e9"
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Fetching 9 files: 100%|██████████| 9/9 [00:00<00:00, 84072.91it/s]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "ERR#: COULD NOT CONVERT TO RS THIS TABLE TO COMPUTE SPANS\n"
     ]
    }
   ],
   "source": [
    "from docling.datamodel.document import ConversionResult\n",
    "from docling.document_converter import DocumentConverter\n",
    "\n",
    "# Instantiate the doc converter\n",
    "doc_converter = DocumentConverter()\n",
    "\n",
    "# Directly pass list of files or streams to `convert_all`\n",
    "conv_results_iter = doc_converter.convert_all(source_urls)  # previously `convert`\n",
    "\n",
    "# Iterate over the generator to get a list of Docling documents\n",
    "docs = [result.document for result in conv_results_iter]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "xHun_P-OCtKd"
   },
   "source": [
    "### Post-process extracted document data\n",
    "#### Perform hierarchical chunking on documents\n",
    "\n",
    "We use Docling's `HierarchicalChunker()` to perform hierarchy-aware chunking of our list of documents. This is meant to preserve some of the structure and relationships within the document, which enables more accurate and relevant retrieval in our RAG pipeline."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "id": "L17ju9xibuIo"
   },
   "outputs": [],
   "source": [
    "from docling_core.transforms.chunker import HierarchicalChunker\n",
    "\n",
    "# Initialize lists for text, and titles\n",
    "texts, titles = [], []\n",
    "\n",
    "chunker = HierarchicalChunker()\n",
    "\n",
    "# Process each document in the list\n",
    "for doc, title in zip(docs, source_titles):  # Pair each document with its title\n",
    "    chunks = list(\n",
    "        chunker.chunk(doc)\n",
    "    )  # Perform hierarchical chunking and get text from chunks\n",
    "    for chunk in chunks:\n",
    "        texts.append(chunk.text)\n",
    "        titles.append(title)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "khbU9R1li2Kj"
   },
   "source": [
    "Because we're splitting the documents into chunks, we'll concatenate the article title to the beginning of each chunk for additional context."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "id": "HNwYV9P57OwF"
   },
   "outputs": [],
   "source": [
    "# Concatenate title and text\n",
    "for i in range(len(texts)):\n",
    "    texts[i] = f\"{titles[i]} {texts[i]}\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "uhLlCpQODaT3"
   },
   "source": [
    "## 💚 Part 2: Weaviate\n",
    "### Create and configure an embedded Weaviate collection"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "ho7xYQTZK5Wk"
   },
   "source": [
    "We'll be using the OpenAI API for both generating the text embeddings and for the generative model in our RAG pipeline. The code below dynamically fetches your API key based on whether you're running this notebook in Google Colab and running it as a regular Jupyter notebook. All you need to do is replace `openai_api_key_var` with the name of your environmental variable name or Colab secret name for the API key.\n",
    "\n",
    "If you're running this notebook in Google Colab, make sure you [add](https://medium.com/@parthdasawant/how-to-use-secrets-in-google-colab-450c38e3ec75) your API key as a secret."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {
    "id": "PD53jOT4roj2"
   },
   "outputs": [],
   "source": [
    "# OpenAI API key variable name\n",
    "openai_api_key_var = \"OPENAI_API_KEY\"  # Replace with the name of your secret/env var\n",
    "\n",
    "# Fetch OpenAI API key\n",
    "try:\n",
    "    # If running in Colab, fetch API key from Secrets\n",
    "    import google.colab\n",
    "    from google.colab import userdata\n",
    "\n",
    "    openai_api_key = userdata.get(openai_api_key_var)\n",
    "    if not openai_api_key:\n",
    "        raise ValueError(f\"Secret '{openai_api_key_var}' not found in Colab secrets.\")\n",
    "except ImportError:\n",
    "    # If not running in Colab, fetch API key from environment variable\n",
    "    import os\n",
    "\n",
    "    openai_api_key = os.getenv(openai_api_key_var)\n",
    "    if not openai_api_key:\n",
    "        raise EnvironmentError(\n",
    "            f\"Environment variable '{openai_api_key_var}' is not set. \"\n",
    "            \"Please define it before running this script.\"\n",
    "        )"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "8G5jZSh6ti3e"
   },
   "source": [
    "[Embedded Weaviate](https://weaviate.io/developers/weaviate/installation/embedded) allows you to spin up a Weaviate instance directly from your application code, without having to use a Docker container. If you're interested in other deployment methods, like using Docker-Compose or Kubernetes, check out this [page](https://weaviate.io/developers/weaviate/installation) in the Weaviate docs."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/"
    },
    "id": "hFUBEZiJUMic",
    "outputId": "0b6534c9-66c9-4a47-9754-103bcc030019"
   },
   "outputs": [],
   "source": [
    "import weaviate\n",
    "\n",
    "# Connect to Weaviate embedded\n",
    "client = weaviate.connect_to_embedded(headers={\"X-OpenAI-Api-Key\": openai_api_key})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "id": "4nu9qM75hrsd"
   },
   "outputs": [],
   "source": [
    "import weaviate.classes.config as wc\n",
    "from weaviate.classes.config import DataType, Property\n",
    "\n",
    "# Define the collection name\n",
    "collection_name = \"docling\"\n",
    "\n",
    "# Delete the collection if it already exists\n",
    "if client.collections.exists(collection_name):\n",
    "    client.collections.delete(collection_name)\n",
    "\n",
    "# Create the collection\n",
    "collection = client.collections.create(\n",
    "    name=collection_name,\n",
    "    vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(\n",
    "        model=\"text-embedding-3-large\",  # Specify your embedding model here\n",
    "    ),\n",
    "    # Enable generative model from Cohere\n",
    "    generative_config=wc.Configure.Generative.openai(\n",
    "        model=\"gpt-4o\"  # Specify your generative model for RAG here\n",
    "    ),\n",
    "    # Define properties of metadata\n",
    "    properties=[\n",
    "        wc.Property(name=\"text\", data_type=wc.DataType.TEXT),\n",
    "        wc.Property(name=\"title\", data_type=wc.DataType.TEXT, skip_vectorization=True),\n",
    "    ],\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "RgMcZDB9Dzfs"
   },
   "source": [
    "### Wrangle data into an acceptable format for Weaviate\n",
    "\n",
    "Transform our data from lists to a list of dictionaries for insertion into our Weaviate collection."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {
    "id": "kttDgwZEsIJQ"
   },
   "outputs": [],
   "source": [
    "# Initialize the data object\n",
    "data = []\n",
    "\n",
    "# Create a dictionary for each row by iterating through the corresponding lists\n",
    "for text, title in zip(texts, titles):\n",
    "    data_point = {\n",
    "        \"text\": text,\n",
    "        \"title\": title,\n",
    "    }\n",
    "    data.append(data_point)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "-4amqRaoD5g0"
   },
   "source": [
    "### Insert data into Weaviate and generate embeddings\n",
    "\n",
    "Embeddings will be generated upon insertion to our Weaviate collection."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/"
    },
    "id": "g8VCYnhbaxcz",
    "outputId": "cc900e56-9fb6-4d4e-ab18-ebd12b1f4201"
   },
   "outputs": [],
   "source": [
    "# Insert text chunks and metadata into vector DB collection\n",
    "response = collection.data.insert_many(data)\n",
    "\n",
    "if response.has_errors:\n",
    "    print(response.errors)\n",
    "else:\n",
    "    print(\"Insert complete.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "KI01PxjuD_XR"
   },
   "source": [
    "### Query the data\n",
    "\n",
    "Here, we perform a simple similarity search to return the most similar embedded chunks to our search query."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/"
    },
    "id": "zbz6nWJc5CSj",
    "outputId": "16aced21-4496-4c91-cc12-d5c9ac983351"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "{'text': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding A distinctive feature of BERT is its unified architecture across different tasks. There is mini-', 'title': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding'}\n",
      "0.6578550338745117\n",
      "{'text': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding We introduce a new language representation model called BERT , which stands for B idirectional E ncoder R epresentations from T ransformers. Unlike recent language representation models (Peters et al., 2018a; Radford et al., 2018), BERT is designed to pretrain deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be finetuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial taskspecific architecture modifications.', 'title': 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding'}\n",
      "0.6696287989616394\n"
     ]
    }
   ],
   "source": [
    "from weaviate.classes.query import MetadataQuery\n",
    "\n",
    "response = collection.query.near_text(\n",
    "    query=\"bert\",\n",
    "    limit=2,\n",
    "    return_metadata=MetadataQuery(distance=True),\n",
    "    return_properties=[\"text\", \"title\"],\n",
    ")\n",
    "\n",
    "for o in response.objects:\n",
    "    print(o.properties)\n",
    "    print(o.metadata.distance)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "elo32iMnEC18"
   },
   "source": [
    "### Perform RAG on parsed articles\n",
    "\n",
    "Weaviate's `generate` module allows you to perform RAG over your embedded data without having to use a separate framework.\n",
    "\n",
    "We specify a prompt that includes the field we want to search through in the database (in this case it's `text`), a query that includes our search term, and the number of retrieved results to use in the generation."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 233
    },
    "id": "7r2LMSX9bO4y",
    "outputId": "84639adf-7783-4d43-94d9-711fb313a168"
   },
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">╭──────────────────────────────────────────────────── Prompt ─────────────────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│</span> Explain how bert works, using only the retrieved context.                                                       <span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;31m╭─\u001b[0m\u001b[1;31m───────────────────────────────────────────────────\u001b[0m\u001b[1;31m Prompt \u001b[0m\u001b[1;31m────────────────────────────────────────────────────\u001b[0m\u001b[1;31m─╮\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m Explain how bert works, using only the retrieved context.                                                       \u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╭─────────────────────────────────────────────── Generated Content ───────────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> BERT, which stands for Bidirectional Encoder Representations from Transformers, is a language representation    <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> model designed to pretrain deep bidirectional representations from unlabeled text. It conditions on both left   <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> and right context in all layers, unlike traditional left-to-right or right-to-left language models. This        <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> pre-training involves two unsupervised tasks. The pre-trained BERT model can then be fine-tuned with just one   <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> additional output layer to create state-of-the-art models for various tasks, such as question answering and     <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> language inference, without needing substantial task-specific architecture modifications. A distinctive feature <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> of BERT is its unified architecture across different tasks.                                                     <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;32m╭─\u001b[0m\u001b[1;32m──────────────────────────────────────────────\u001b[0m\u001b[1;32m Generated Content \u001b[0m\u001b[1;32m──────────────────────────────────────────────\u001b[0m\u001b[1;32m─╮\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m BERT, which stands for Bidirectional Encoder Representations from Transformers, is a language representation    \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m model designed to pretrain deep bidirectional representations from unlabeled text. It conditions on both left   \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m and right context in all layers, unlike traditional left-to-right or right-to-left language models. This        \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m pre-training involves two unsupervised tasks. The pre-trained BERT model can then be fine-tuned with just one   \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m additional output layer to create state-of-the-art models for various tasks, such as question answering and     \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m language inference, without needing substantial task-specific architecture modifications. A distinctive feature \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m of BERT is its unified architecture across different tasks.                                                     \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from rich.console import Console\n",
    "from rich.panel import Panel\n",
    "\n",
    "# Create a prompt where context from the Weaviate collection will be injected\n",
    "prompt = \"Explain how {text} works, using only the retrieved context.\"\n",
    "query = \"bert\"\n",
    "\n",
    "response = collection.generate.near_text(\n",
    "    query=query, limit=3, grouped_task=prompt, return_properties=[\"text\", \"title\"]\n",
    ")\n",
    "\n",
    "# Prettify the output using Rich\n",
    "console = Console()\n",
    "\n",
    "console.print(\n",
    "    Panel(f\"{prompt}\".replace(\"{text}\", query), title=\"Prompt\", border_style=\"bold red\")\n",
    ")\n",
    "console.print(\n",
    "    Panel(response.generated, title=\"Generated Content\", border_style=\"bold green\")\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 233
    },
    "id": "Dtju3oCiDOdD",
    "outputId": "2f0f0cf8-0305-40cc-8409-07036c101938"
   },
   "outputs": [
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">╭──────────────────────────────────────────────────── Prompt ─────────────────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│</span> Explain how a generative adversarial net works, using only the retrieved context.                               <span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #800000; text-decoration-color: #800000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;31m╭─\u001b[0m\u001b[1;31m───────────────────────────────────────────────────\u001b[0m\u001b[1;31m Prompt \u001b[0m\u001b[1;31m────────────────────────────────────────────────────\u001b[0m\u001b[1;31m─╮\u001b[0m\n",
       "\u001b[1;31m│\u001b[0m Explain how a generative adversarial net works, using only the retrieved context.                               \u001b[1;31m│\u001b[0m\n",
       "\u001b[1;31m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "text/html": [
       "<pre style=\"white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\"><span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╭─────────────────────────────────────────────── Generated Content ───────────────────────────────────────────────╮</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> Generative Adversarial Nets (GANs) operate within an adversarial framework where two models are trained         <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> simultaneously: a generative model (G) and a discriminative model (D). The generative model aims to capture the <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> data distribution and generate samples that mimic real data, while the discriminative model's task is to        <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> distinguish between samples from the real data and those generated by G. This setup is akin to a game where the <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> generative model acts like counterfeiters trying to produce indistinguishable fake currency, and the            <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> discriminative model acts like the police trying to detect these counterfeits.                                  <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>                                                                                                                 <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> The training process involves a minimax two-player game where G tries to maximize the probability of D making a <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> mistake, while D tries to minimize it. When both models are defined by multilayer perceptrons, they can be      <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> trained using backpropagation without the need for Markov chains or approximate inference networks. The         <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> ultimate goal is for G to perfectly replicate the training data distribution, making D's output equal to 1/2    <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> everywhere, indicating it cannot distinguish between real and generated data. This framework allows for         <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> specific training algorithms and optimization techniques, such as backpropagation and dropout, to be            <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span> effectively utilized.                                                                                           <span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">│</span>\n",
       "<span style=\"color: #008000; text-decoration-color: #008000; font-weight: bold\">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>\n",
       "</pre>\n"
      ],
      "text/plain": [
       "\u001b[1;32m╭─\u001b[0m\u001b[1;32m──────────────────────────────────────────────\u001b[0m\u001b[1;32m Generated Content \u001b[0m\u001b[1;32m──────────────────────────────────────────────\u001b[0m\u001b[1;32m─╮\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m Generative Adversarial Nets (GANs) operate within an adversarial framework where two models are trained         \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m simultaneously: a generative model (G) and a discriminative model (D). The generative model aims to capture the \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m data distribution and generate samples that mimic real data, while the discriminative model's task is to        \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m distinguish between samples from the real data and those generated by G. This setup is akin to a game where the \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m generative model acts like counterfeiters trying to produce indistinguishable fake currency, and the            \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m discriminative model acts like the police trying to detect these counterfeits.                                  \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m                                                                                                                 \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m The training process involves a minimax two-player game where G tries to maximize the probability of D making a \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m mistake, while D tries to minimize it. When both models are defined by multilayer perceptrons, they can be      \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m trained using backpropagation without the need for Markov chains or approximate inference networks. The         \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m ultimate goal is for G to perfectly replicate the training data distribution, making D's output equal to 1/2    \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m everywhere, indicating it cannot distinguish between real and generated data. This framework allows for         \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m specific training algorithms and optimization techniques, such as backpropagation and dropout, to be            \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m│\u001b[0m effectively utilized.                                                                                           \u001b[1;32m│\u001b[0m\n",
       "\u001b[1;32m╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\u001b[0m\n"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "# Create a prompt where context from the Weaviate collection will be injected\n",
    "prompt = \"Explain how {text} works, using only the retrieved context.\"\n",
    "query = \"a generative adversarial net\"\n",
    "\n",
    "response = collection.generate.near_text(\n",
    "    query=query, limit=3, grouped_task=prompt, return_properties=[\"text\", \"title\"]\n",
    ")\n",
    "\n",
    "# Prettify the output using Rich\n",
    "console = Console()\n",
    "\n",
    "console.print(\n",
    "    Panel(f\"{prompt}\".replace(\"{text}\", query), title=\"Prompt\", border_style=\"bold red\")\n",
    ")\n",
    "console.print(\n",
    "    Panel(response.generated, title=\"Generated Content\", border_style=\"bold green\")\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "7tGz49nfUegG"
   },
   "source": [
    "We can see that our RAG pipeline performs relatively well for simple queries, especially given the small size of the dataset. Scaling this method for converting a larger sample of PDFs would require more compute (GPUs) and a more advanced deployment of Weaviate (like Docker, Kubernetes, or Weaviate Cloud). For more information on available Weaviate configurations, check out the [documetation](https://weaviate.io/developers/weaviate/starter-guides/which-weaviate)."
   ]
  }
 ],
 "metadata": {
  "accelerator": "GPU",
  "colab": {
   "gpuType": "T4",
   "provenance": []
  },
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}

```
</content>
</file_31>

<file_32>
<path>examples/rapidocr_with_custom_models.py</path>
<content>
```python
import os

from huggingface_hub import snapshot_download

from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import (
    ConversionResult,
    DocumentConverter,
    InputFormat,
    PdfFormatOption,
)


def main():
    # Source document to convert
    source = "https://arxiv.org/pdf/2408.09869v4"

    # Download RappidOCR models from HuggingFace
    print("Downloading RapidOCR models")
    download_path = snapshot_download(repo_id="SWHL/RapidOCR")

    # Setup RapidOcrOptions for english detection
    det_model_path = os.path.join(
        download_path, "PP-OCRv4", "en_PP-OCRv3_det_infer.onnx"
    )
    rec_model_path = os.path.join(
        download_path, "PP-OCRv4", "ch_PP-OCRv4_rec_server_infer.onnx"
    )
    cls_model_path = os.path.join(
        download_path, "PP-OCRv3", "ch_ppocr_mobile_v2.0_cls_train.onnx"
    )
    ocr_options = RapidOcrOptions(
        det_model_path=det_model_path,
        rec_model_path=rec_model_path,
        cls_model_path=cls_model_path,
    )

    pipeline_options = PdfPipelineOptions(
        ocr_options=ocr_options,
    )

    # Convert the document
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            ),
        },
    )

    conversion_result: ConversionResult = converter.convert(source=source)
    doc = conversion_result.document
    md = doc.export_to_markdown()
    print(md)


if __name__ == "__main__":
    main()

```
</content>
</file_32>

<file_33>
<path>examples/retrieval_qdrant.ipynb</path>
<content>
```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<a href=\"https://colab.research.google.com/github/DS4SD/docling/blob/main/docs/examples/hybrid_rag_qdrant\n",
    ".ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Retrieval with Qdrant"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "| Step | Tech | Execution | \n",
    "| --- | --- | --- |\n",
    "| Embedding | FastEmbed | 💻 Local |\n",
    "| Vector store | Qdrant | 💻 Local |"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Overview"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This example demonstrates using Docling with [Qdrant](https://qdrant.tech/) to perform a hybrid search across your documents using dense and sparse vectors.\n",
    "\n",
    "We'll chunk the documents using Docling before adding them to a Qdrant collection. By limiting the length of the chunks, we can preserve the meaning in each vector embedding."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Setup"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "- 👉 Qdrant client uses [FastEmbed](https://github.com/qdrant/fastembed) to generate vector embeddings. You can install the `fastembed-gpu` package if you've got the hardware to support it."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    }
   ],
   "source": [
    "%pip install --no-warn-conflicts -q qdrant-client docling fastembed"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Let's import all the classes we'll be working with."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "from qdrant_client import QdrantClient\n",
    "\n",
    "from docling.chunking import HybridChunker\n",
    "from docling.datamodel.base_models import InputFormat\n",
    "from docling.document_converter import DocumentConverter"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "- For Docling, we'll set the  allowed formats to HTML since we'll only be working with webpages in this tutorial.\n",
    "- If we set a sparse model, Qdrant client will fuse the dense and sparse results using RRF. [Reference](https://qdrant.tech/documentation/tutorials/hybrid-search-fastembed/)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/pva/work/github.com/DS4SD/docling/.venv/lib/python3.12/site-packages/huggingface_hub/utils/tqdm.py:155: UserWarning: Cannot enable progress bars: environment variable `HF_HUB_DISABLE_PROGRESS_BARS=1` is set and has priority.\n",
      "  warnings.warn(\n"
     ]
    }
   ],
   "source": [
    "COLLECTION_NAME = \"docling\"\n",
    "\n",
    "doc_converter = DocumentConverter(allowed_formats=[InputFormat.HTML])\n",
    "client = QdrantClient(location=\":memory:\")\n",
    "# The :memory: mode is a Python imitation of Qdrant's APIs for prototyping and CI.\n",
    "# For production deployments, use the Docker image: docker run -p 6333:6333 qdrant/qdrant\n",
    "# client = QdrantClient(location=\"http://localhost:6333\")\n",
    "\n",
    "client.set_model(\"sentence-transformers/all-MiniLM-L6-v2\")\n",
    "client.set_sparse_model(\"Qdrant/bm25\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can now download and chunk the document using Docling. For demonstration, we'll use an article about chunking strategies :)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "result = doc_converter.convert(\n",
    "    \"https://www.sagacify.com/news/a-guide-to-chunking-strategies-for-retrieval-augmented-generation-rag\"\n",
    ")\n",
    "documents, metadatas = [], []\n",
    "for chunk in HybridChunker().chunk(result.document):\n",
    "    documents.append(chunk.text)\n",
    "    metadatas.append(chunk.meta.export_json_dict())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Let's now upload the documents to Qdrant.\n",
    "\n",
    "- The `add()` method batches the documents and uses FastEmbed to generate vector embeddings on our machine."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "_ = client.add(\n",
    "    collection_name=COLLECTION_NAME,\n",
    "    documents=documents,\n",
    "    metadata=metadatas,\n",
    "    batch_size=64,\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Retrieval"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "points = client.query(\n",
    "    collection_name=COLLECTION_NAME,\n",
    "    query_text=\"Can I split documents?\",\n",
    "    limit=10,\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "=== 0 ===\n",
      "Have you ever wondered how we, humans, would chunk? Here's a breakdown of a possible way a human would process a new document:\n",
      "1. We start at the top of the document, treating the first part as a chunk.\n",
      "   2. We continue down the document, deciding if a new sentence or piece of information belongs with the first chunk or should start a new one.\n",
      "    3. We keep this up until we reach the end of the document.\n",
      "The ultimate dream? Having an agent do this for you. But slow down! This approach is still being tested and isn't quite ready for the big leagues due to the time it takes to process multiple LLM calls and the cost of those calls. There's no implementation available in public libraries just yet. However, Greg Kamradt has his version available here.\n",
      "\n",
      "=== 1 ===\n",
      "Document Specific Chunking is a strategy that respects the document's structure. Rather than using a set number of characters or a recursive process, it creates chunks that align with the logical sections of the document, like paragraphs or subsections. This approach maintains the original author's organization of content and helps keep the text coherent. It makes the retrieved information more relevant and useful, particularly for structured documents with clearly defined sections.\n",
      "Document Specific Chunking can handle a variety of document formats, such as:\n",
      "Markdown\n",
      "HTML\n",
      "Python\n",
      "etc\n",
      "Here we’ll take Markdown as our example and use a modified version of our first sample text:\n",
      "‍\n",
      "The result is the following:\n",
      "You can see here that with a chunk size of 105, the Markdown structure of the document is taken into account, and the chunks thus preserve the semantics of the text!\n",
      "\n",
      "=== 2 ===\n",
      "And there you have it! These chunking strategies are like a personal toolbox when it comes to implementing Retrieval Augmented Generation. They're a ton of ways to slice and dice text, each with its unique features and quirks. This variety gives you the freedom to pick the strategy that suits your project best, allowing you to tailor your approach to perfectly fit the unique needs of your work.\n",
      "To put these strategies into action, there's a whole array of tools and libraries at your disposal. For example, llama_index is a fantastic tool that lets you create document indices and retrieve chunked documents. Let's not forget LangChain, another remarkable tool that makes implementing chunking strategies a breeze, particularly when dealing with multi-language data. Diving into these tools and understanding how they can work in harmony with the chunking strategies we've discussed is a crucial part of mastering Retrieval Augmented Generation.\n",
      "By the way, if you're eager to experiment with your own examples using the chunking visualisation tool featured in this blog, feel free to give it a try! You can access it right here. Enjoy, and happy chunking! 😉\n",
      "\n",
      "=== 3 ===\n",
      "Retrieval Augmented Generation (RAG) has been a hot topic in understanding, interpreting, and generating text with AI for the last few months. It's like a wonderful union of retrieval-based and generative models, creating a playground for researchers, data scientists, and natural language processing enthusiasts, like you and me.\n",
      "To truly control the results produced by our RAG, we need to understand chunking strategies and their role in the process of retrieving and generating text. Indeed, each chunking strategy enhances RAG's effectiveness in its unique way.\n",
      "The goal of chunking is, as its name says, to chunk the information into multiple smaller pieces in order to store it in a more efficient and meaningful way. This allows the retrieval to capture pieces of information that are more related to the question at hand, and the generation to be more precise, but also less costly, as only a part of a document will be included in the LLM prompt, instead of the whole document.\n",
      "Let's explore some chunking strategies together.\n",
      "The methods mentioned in the article you're about to read usually make use of two key parameters. First, we have [chunk_size]— which controls the size of your text chunks. Then there's [chunk_overlap], which takes care of how much text overlaps between one chunk and the next.\n",
      "\n",
      "=== 4 ===\n",
      "Semantic Chunking considers the relationships within the text. It divides the text into meaningful, semantically complete chunks. This approach ensures the information's integrity during retrieval, leading to a more accurate and contextually appropriate outcome.\n",
      "Semantic chunking involves taking the embeddings of every sentence in the document, comparing the similarity of all sentences with each other, and then grouping sentences with the most similar embeddings together.\n",
      "By focusing on the text's meaning and context, Semantic Chunking significantly enhances the quality of retrieval. It's a top-notch choice when maintaining the semantic integrity of the text is vital.\n",
      "However, this method does require more effort and is notably slower than the previous ones.\n",
      "On our example text, since it is quite short and does not expose varied subjects, this method would only generate a single chunk.\n",
      "\n",
      "=== 5 ===\n",
      "Language models used in the rest of your possible RAG pipeline have a token limit, which should not be exceeded. When dividing your text into chunks, it's advisable to count the number of tokens. Plenty of tokenizers are available. To ensure accuracy, use the same tokenizer for counting tokens as the one used in the language model.\n",
      "Consequently, there are also splitters available for this purpose.\n",
      "For instance, by using the [SpacyTextSplitter] from LangChain, the following chunks are created:\n",
      "‍\n",
      "\n",
      "=== 6 ===\n",
      "First things first, we have Character Chunking. This strategy divides the text into chunks based on a fixed number of characters. Its simplicity makes it a great starting point, but it can sometimes disrupt the text's flow, breaking sentences or words in unexpected places. Despite its limitations, it's a great stepping stone towards more advanced methods.\n",
      "Now let’s see that in action with an example. Imagine a text that reads:\n",
      "If we decide to set our chunk size to 100 and no chunk overlap, we'd end up with the following chunks. As you can see, Character Chunking can lead to some intriguing, albeit sometimes nonsensical, results, cutting some of the sentences in their middle.\n",
      "By choosing a smaller chunk size,  we would obtain more chunks, and by setting a bigger chunk overlap, we could obtain something like this:\n",
      "‍\n",
      "Also, by default this method creates chunks character by character based on the empty character [’ ’]. But you can specify a different one in order to chunk on something else, even a complete word! For instance, by specifying [' '] as the separator, you can avoid cutting words in their middle.\n",
      "\n",
      "=== 7 ===\n",
      "Next, let's take a look at Recursive Character Chunking. Based on the basic concept of Character Chunking, this advanced version takes it up a notch by dividing the text into chunks until a certain condition is met, such as reaching a minimum chunk size. This method ensures that the chunking process aligns with the text's structure, preserving more meaning. Its adaptability makes Recursive Character Chunking great for texts with varied structures.\n",
      "Again, let’s use the same example in order to illustrate this method. With a chunk size of 100, and the default settings for the other parameters, we obtain the following chunks:\n",
      "\n"
     ]
    }
   ],
   "source": [
    "for i, point in enumerate(points):\n",
    "    print(f\"=== {i} ===\")\n",
    "    print(point.document)\n",
    "    print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

```
</content>
</file_33>

<file_34>
<path>examples/run_md.py</path>
<content>
```python
import json
import logging
import os
from pathlib import Path

import yaml

from docling.backend.md_backend import MarkdownDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


def main():
    input_paths = [Path("README.md")]

    for path in input_paths:
        in_doc = InputDocument(
            path_or_stream=path,
            format=InputFormat.PDF,
            backend=MarkdownDocumentBackend,
        )
        mdb = MarkdownDocumentBackend(in_doc=in_doc, path_or_stream=path)
        document = mdb.convert()

        out_path = Path("scratch")
        print(
            f"Document {path} converted." f"\nSaved markdown output to: {str(out_path)}"
        )

        # Export Docling document format to markdowndoc:
        fn = os.path.basename(path)

        with (out_path / f"{fn}.md").open("w") as fp:
            fp.write(document.export_to_markdown())

        with (out_path / f"{fn}.json").open("w") as fp:
            fp.write(json.dumps(document.export_to_dict()))

        with (out_path / f"{fn}.yaml").open("w") as fp:
            fp.write(yaml.safe_dump(document.export_to_dict()))


if __name__ == "__main__":
    main()

```
</content>
</file_34>

<file_35>
<path>examples/run_with_accelerator.py</path>
<content>
```python
from pathlib import Path

from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption


def main():
    input_doc = Path("./tests/data/2206.01062.pdf")

    # Explicitly set the accelerator
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.AUTO
    # )
    accelerator_options = AcceleratorOptions(
        num_threads=8, device=AcceleratorDevice.CPU
    )
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.MPS
    # )
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.CUDA
    # )

    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = accelerator_options
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )

    # Enable the profiling to measure the time spent
    settings.debug.profile_pipeline_timings = True

    # Convert the document
    conversion_result = converter.convert(input_doc)
    doc = conversion_result.document

    # List with total time per document
    doc_conversion_secs = conversion_result.timings["pipeline_total"].times

    md = doc.export_to_markdown()
    print(md)
    print(f"Conversion secs: {doc_conversion_secs}")


if __name__ == "__main__":
    main()

```
</content>
</file_35>

<file_36>
<path>examples/run_with_formats.py</path>
<content>
```python
import json
import logging
from pathlib import Path

import yaml

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

_log = logging.getLogger(__name__)


def main():
    input_paths = [
        Path("README.md"),
        Path("tests/data/html/wiki_duck.html"),
        Path("tests/data/docx/word_sample.docx"),
        Path("tests/data/docx/lorem_ipsum.docx"),
        Path("tests/data/pptx/powerpoint_sample.pptx"),
        Path("tests/data/2305.03393v1-pg9-img.png"),
        Path("tests/data/2206.01062.pdf"),
        Path("tests/data/test_01.asciidoc"),
        Path("tests/data/test_01.asciidoc"),
    ]

    ## for defaults use:
    # doc_converter = DocumentConverter()

    ## to customize use:

    doc_converter = (
        DocumentConverter(  # all of the below is optional, has internal defaults.
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.IMAGE,
                InputFormat.DOCX,
                InputFormat.HTML,
                InputFormat.PPTX,
                InputFormat.ASCIIDOC,
                InputFormat.MD,
            ],  # whitelist formats, non-matching files are ignored.
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=StandardPdfPipeline, backend=PyPdfiumDocumentBackend
                ),
                InputFormat.DOCX: WordFormatOption(
                    pipeline_cls=SimplePipeline  # , backend=MsWordDocumentBackend
                ),
            },
        )
    )

    conv_results = doc_converter.convert_all(input_paths)

    for res in conv_results:
        out_path = Path("scratch")
        print(
            f"Document {res.input.file.name} converted."
            f"\nSaved markdown output to: {str(out_path)}"
        )
        _log.debug(res.document._export_to_indented_text(max_text_len=16))
        # Export Docling document format to markdowndoc:
        with (out_path / f"{res.input.file.stem}.md").open("w") as fp:
            fp.write(res.document.export_to_markdown())

        with (out_path / f"{res.input.file.stem}.json").open("w") as fp:
            fp.write(json.dumps(res.document.export_to_dict()))

        with (out_path / f"{res.input.file.stem}.yaml").open("w") as fp:
            fp.write(yaml.safe_dump(res.document.export_to_dict()))


if __name__ == "__main__":
    main()

```
</content>
</file_36>

<file_37>
<path>examples/tesseract_lang_detection.py</path>
<content>
```python
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption


def main():
    input_doc = Path("./tests/data/2206.01062.pdf")

    # Set lang=["auto"] with a tesseract OCR engine: TesseractOcrOptions, TesseractCliOcrOptions
    # ocr_options = TesseractOcrOptions(lang=["auto"])
    ocr_options = TesseractCliOcrOptions(lang=["auto"])

    pipeline_options = PdfPipelineOptions(
        do_ocr=True, force_full_page_ocr=True, ocr_options=ocr_options
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )

    doc = converter.convert(input_doc).document
    md = doc.export_to_markdown()
    print(md)


if __name__ == "__main__":
    main()

```
</content>
</file_37>

<file_38>
<path>examples/translate.py</path>
<content>
```python
import logging
import time
from pathlib import Path

from docling_core.types.doc import ImageRefMode, PictureItem, TableItem, TextItem

from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0


# FIXME: put in your favorite translation code ....
def translate(text: str, src: str = "en", dest: str = "de"):

    _log.warning("!!! IMPLEMENT HERE YOUR FAVORITE TRANSLATION CODE!!!")
    # from googletrans import Translator

    # Initialize the translator
    # translator = Translator()

    # Translate text from English to German
    # text = "Hello, how are you?"
    # translated = translator.translate(text, src="en", dest="de")

    return text


def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("./tests/data/2206.01062.pdf")
    output_dir = Path("scratch")

    # Important: For operating with page images, we must keep them, otherwise the DocumentConverter
    # will destroy them for cleaning up memory.
    # This is done by setting PdfPipelineOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    # The PdfPipelineOptions.generate_* are the selectors for the document elements which will be enriched
    # with the image field
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)
    conv_doc = conv_res.document

    # Save markdown with embedded pictures in original text
    md_filename = output_dir / f"{doc_filename}-with-images-orig.md"
    conv_doc.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TextItem):
            element.orig = element.text
            element.text = translate(text=element.text)

        elif isinstance(element, TableItem):
            for cell in element.data.table_cells:
                cell.text = translate(text=element.text)

    # Save markdown with embedded pictures in translated text
    md_filename = output_dir / f"{doc_filename}-with-images-translated.md"
    conv_doc.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

```
</content>
</file_38>

<file_39>
<path>faq.md</path>
<content>
```markdown
# FAQ

This is a collection of FAQ collected from the user questions on <https://github.com/DS4SD/docling/discussions>.


??? question "Is Python 3.13 supported?"

    ### Is Python 3.13 supported?

    Python 3.13 is supported from Docling 2.18.0.


??? question "Install conflicts with numpy (python 3.13)"

    ### Install conflicts with numpy (python 3.13)

    When using `docling-ibm-models>=2.0.7` and `deepsearch-glm>=0.26.2` these issues should not show up anymore.
    Docling supports numpy versions `>=1.24.4,<3.0.0` which should match all usages.

    **For older versions**

    This has been observed installing docling and langchain via poetry.

    ```
    ...
    Thus, docling (>=2.7.0,<3.0.0) requires numpy (>=1.26.4,<2.0.0).
    So, because ... depends on both numpy (>=2.0.2,<3.0.0) and docling (^2.7.0), version solving failed.
    ```

    Numpy is only adding Python 3.13 support starting in some 2.x.y version. In order to prepare for 3.13, Docling depends on a 2.x.y for 3.13, otherwise depending an 1.x.y version. If you are allowing 3.13 in your pyproject.toml, Poetry will try to find some way to reconcile Docling's numpy version for 3.13 (some 2.x.y) with LangChain's version for that (some 1.x.y) — leading to the error above.

    Check if Python 3.13 is among the Python versions allowed by your pyproject.toml and if so, remove it and try again.
    E.g., if you have python = "^3.10", use python = ">=3.10,<3.13" instead.

    If you want to retain compatibility with python 3.9-3.13, you can also use a selector in pyproject.toml similar to the following

    ```toml
    numpy = [
        { version = "^2.1.0", markers = 'python_version >= "3.13"' },
        { version = "^1.24.4", markers = 'python_version < "3.13"' },
    ]
    ```

    Source: Issue [#283](https://github.com/DS4SD/docling/issues/283#issuecomment-2465035868)


??? question "Are text styles (bold, underline, etc) supported?"

    ### Are text styles (bold, underline, etc) supported?

    Currently text styles are not supported in the `DoclingDocument` format.
    If you are interest in contributing this feature, please open a discussion topic to brainstorm on the design.

    _Note: this is not a simple topic_


??? question "How do I run completely offline?"

    ### How do I run completely offline?

    Docling is not using any remote service, hence it can run in completely isolated air-gapped environments.

    The only requirement is pointing the Docling runtime to the location where the model artifacts have been stored.

    For example

    ```py

    pipeline_options = PdfPipelineOptions(artifacts_path="your location")
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    ```

    Source: Issue [#326](https://github.com/DS4SD/docling/issues/326)


??? question " Which model weights are needed to run Docling?"
    ### Which model weights are needed to run Docling?

    Model weights are needed for the AI models used in the PDF pipeline. Other document types (docx, pptx, etc) do not have any such requirement.

    For processing PDF documents, Docling requires the model weights from <https://huggingface.co/ds4sd/docling-models>.

    When OCR is enabled, some engines also require model artifacts. For example EasyOCR, for which Docling has [special pipeline options](https://github.com/DS4SD/docling/blob/main/docling/datamodel/pipeline_options.py#L68) to control the runtime behavior.


??? question "SSL error downloading model weights"

    ### SSL error downloading model weights

    ```
    URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)>
    ```

    Similar SSL download errors have been observed by some users. This happens when model weights are fetched from Hugging Face.
    The error could happen when the python environment doesn't have an up-to-date list of trusted certificates.

    Possible solutions were

    - Update to the latest version of [certifi](https://pypi.org/project/certifi/), i.e. `pip install --upgrade certifi`
    - Use [pip-system-certs](https://pypi.org/project/pip-system-certs/) to use the latest trusted certificates on your system.
    - Set environment variables `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` to the value of `python -m certifi`:
        ```
        CERT_PATH=$(python -m certifi)
        export SSL_CERT_FILE=${CERT_PATH}
        export REQUESTS_CA_BUNDLE=${CERT_PATH}
        ```


??? question "Which OCR languages are supported?"

    ### Which OCR languages are supported?

    Docling supports multiple OCR engine, each one has its own list of supported languages.
    Here is a collection of links to the original OCR engine's documentation listing the OCR languages.

    - [EasyOCR](https://www.jaided.ai/easyocr/)
    - [Tesseract](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)
    - [RapidOCR](https://rapidai.github.io/RapidOCRDocs/blog/2022/09/28/%E6%94%AF%E6%8C%81%E8%AF%86%E5%88%AB%E8%AF%AD%E8%A8%80/)
    - [Mac OCR](https://github.com/straussmaximilian/ocrmac/tree/main?tab=readme-ov-file#example-select-language-preference)

    Setting the OCR language in Docling is done via the OCR pipeline options:

    ```py
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    pipeline_options = PdfPipelineOptions()
    pipeline_options.ocr_options.lang = ["fr", "de", "es", "en"]  # example of languages for EasyOCR
    ```


??? Some images are missing from MS Word and Powerpoint"

    ### Some images are missing from MS Word and Powerpoint

    The image processing library used by Docling is able to handle embedded WMF images only on Windows platform.
    If you are on other operaring systems, these images will be ignored.

```
</content>
</file_39>

<file_40>
<path>index.md</path>
<content>
```markdown
<p align="center">
  <img loading="lazy" alt="Docling" src="assets/docling_processing.png" width="100%" />
  <a href="https://trendshift.io/repositories/12132" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12132" alt="DS4SD%2Fdocling | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

[![arXiv](https://img.shields.io/badge/arXiv-2408.09869-b31b1b.svg)](https://arxiv.org/abs/2408.09869)
[![PyPI version](https://img.shields.io/pypi/v/docling)](https://pypi.org/project/docling/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docling)](https://pypi.org/project/docling/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License MIT](https://img.shields.io/github/license/DS4SD/docling)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/badge/docling/month)](https://pepy.tech/projects/docling)

Docling simplifies document processing, parsing diverse formats — including advanced PDF understanding — and providing seamless integrations with the gen AI ecosystem.

## Features

* 🗂️ Parsing of [multiple document formats][supported_formats] incl. PDF, DOCX, XLSX, HTML, images, and more
* 📑 Advanced PDF understanding incl. page layout, reading order, table structure, code, formulas, image classification, and more
* 🧬 Unified, expressive [DoclingDocument][docling_document] representation format
* ↪️ Various [export formats][supported_formats] and options, including Markdown, HTML, and lossless JSON
* 🔒 Local execution capabilities for sensitive data and air-gapped environments
* 🤖 Plug-and-play [integrations][integrations] incl. LangChain, LlamaIndex, Crew AI & Haystack for agentic AI
* 🔍 Extensive OCR support for scanned PDFs and images
* 💻 Simple and convenient CLI

### Coming soon

* 📝 Metadata extraction, including title, authors, references & language
* 📝 Inclusion of Visual Language Models ([SmolDocling](https://huggingface.co/blog/smolervlm#smoldocling))
* 📝 Chart understanding (Barchart, Piechart, LinePlot, etc)
* 📝 Complex chemistry understanding (Molecular structures)

## Get started

<div class="grid">
  <a href="concepts/" class="card"><b>Concepts</b><br />Learn Docling fundamendals</a>
  <a href="examples/" class="card"><b>Examples</b><br />Try out recipes for various use cases, including conversion, RAG, and more</a>
  <a href="integrations/" class="card"><b>Integrations</b><br />Check out integrations with popular frameworks and tools</a>
  <a href="reference/document_converter/" class="card"><b>Reference</b><br />See more API details</a>
</div>

## IBM ❤️ Open Source AI

Docling has been brought to you by IBM.

[supported_formats]: ./supported_formats.md
[docling_document]: ./concepts/docling_document.md
[integrations]: ./integrations/index.md

```
</content>
</file_40>

<file_41>
<path>installation.md</path>
<content>
```markdown
To use Docling, simply install `docling` from your Python package manager, e.g. pip:
```bash
pip install docling
```

Works on macOS, Linux, and Windows, with support for both x86_64 and arm64 architectures.

??? "Alternative PyTorch distributions"

    The Docling models depend on the [PyTorch](https://pytorch.org/) library.
    Depending on your architecture, you might want to use a different distribution of `torch`.
    For example, you might want support for different accelerator or for a cpu-only version.
    All the different ways for installing `torch` are listed on their website <https://pytorch.org/>.

    One common situation is the installation on Linux systems with cpu-only support.
    In this case, we suggest the installation of Docling with the following options

    ```bash
    # Example for installing on the Linux cpu-only version
    pip install docling --extra-index-url https://download.pytorch.org/whl/cpu
    ```

??? "Alternative OCR engines"

    Docling supports multiple OCR engines for processing scanned documents. The current version provides
    the following engines.

    | Engine | Installation | Usage |
    | ------ | ------------ | ----- |
    | [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Default in Docling or via `pip install easyocr`. | `EasyOcrOptions` |
    | Tesseract | System dependency. See description for Tesseract and Tesserocr below.  | `TesseractOcrOptions` |
    | Tesseract CLI | System dependency. See description below. | `TesseractCliOcrOptions` |
    | OcrMac | System dependency. See description below. | `OcrMacOptions` |
    | [RapidOCR](https://github.com/RapidAI/RapidOCR) | Extra feature not included in Default Docling installation can be installed via `pip install rapidocr_onnxruntime` | `RapidOcrOptions` |

    The Docling `DocumentConverter` allows to choose the OCR engine with the `ocr_options` settings. For example

    ```python
    from docling.datamodel.base_models import ConversionStatus, PipelineOptions
    from docling.datamodel.pipeline_options import PipelineOptions, EasyOcrOptions, TesseractOcrOptions
    from docling.document_converter import DocumentConverter

    pipeline_options = PipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.ocr_options = TesseractOcrOptions()  # Use Tesseract

    doc_converter = DocumentConverter(
        pipeline_options=pipeline_options,
    )
    ```

    <h3>Tesseract installation</h3>

    [Tesseract](https://github.com/tesseract-ocr/tesseract) is a popular OCR engine which is available
    on most operating systems. For using this engine with Docling, Tesseract must be installed on your
    system, using the packaging tool of your choice. Below we provide example commands.
    After installing Tesseract you are expected to provide the path to its language files using the
    `TESSDATA_PREFIX` environment variable (note that it must terminate with a slash `/`).

    === "macOS (via [Homebrew](https://brew.sh/))"

        ```console
        brew install tesseract leptonica pkg-config
        TESSDATA_PREFIX=/opt/homebrew/share/tessdata/
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    === "Debian-based"

        ```console
        apt-get install tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev pkg-config
        TESSDATA_PREFIX=$(dpkg -L tesseract-ocr-eng | grep tessdata$)
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    === "RHEL"

        ```console
        dnf install tesseract tesseract-devel tesseract-langpack-eng leptonica-devel
        TESSDATA_PREFIX=/usr/share/tesseract/tessdata/
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    <h3>Linking to Tesseract</h3>
    The most efficient usage of the Tesseract library is via linking. Docling is using
    the [Tesserocr](https://github.com/sirfz/tesserocr) package for this.

    If you get into installation issues of Tesserocr, we suggest using the following
    installation options:

    ```console
    pip uninstall tesserocr
    pip install --no-binary :all: tesserocr
    ```

    <h3>ocrmac installation</h3>

    [ocrmac](https://github.com/straussmaximilian/ocrmac) is using
    Apple's vision(or livetext) framework as OCR backend.
    For using this engine with Docling, ocrmac must be installed on your system.
    This only works on macOS systems with newer macOS versions (10.15+).

    ```console
    pip install ocrmac
    ```

## Development setup

To develop Docling features, bugfixes etc., install as follows from your local clone's root dir:

```bash
poetry install --all-extras
```

```
</content>
</file_41>

<file_42>
<path>integrations/bee.md</path>
<content>
```markdown
Docling is available as an extraction backend in the [Bee][github] framework.

- 💻 [Bee GitHub][github]
- 📖 [Bee docs][docs]
- 📦 [Bee NPM][package]

[github]: https://github.com/i-am-bee
[docs]: https://i-am-bee.github.io/bee-agent-framework/
[package]: https://www.npmjs.com/package/bee-agent-framework

```
</content>
</file_42>

<file_43>
<path>integrations/cloudera.md</path>
<content>
```markdown
Docling is available in [Cloudera](https://www.cloudera.com/) through the *RAG Studio*
Accelerator for Machine Learning Projects (AMP).

- 💻 [RAG Studio AMP GitHub][github]

[github]: https://github.com/cloudera/CML_AMP_RAG_Studio

```
</content>
</file_43>

<file_44>
<path>integrations/crewai.md</path>
<content>
```markdown
Docling is available in [CrewAI](https://www.crewai.com/) as the `CrewDoclingSource`
knowledge source.

- 💻 [Crew AI GitHub][github]
- 📖 [Crew AI knowledge docs][docs]
- 📦 [Crew AI PyPI][package]

[github]: https://github.com/crewAIInc/crewAI/
[docs]: https://docs.crewai.com/concepts/knowledge
[package]: https://pypi.org/project/crewai/

```
</content>
</file_44>

<file_45>
<path>integrations/data_prep_kit.md</path>
<content>
```markdown
Docling is used by the [Data Prep Kit](https://ibm.github.io/data-prep-kit/) open-source toolkit for preparing unstructured data for LLM application development ranging from laptop scale to datacenter scale.

## Components
### PDF ingestion to Parquet
- 💻 [PDF-to-Parquet GitHub](https://github.com/IBM/data-prep-kit/tree/dev/transforms/language/pdf2parquet)
- 📖 [PDF-to-Parquet docs](https://ibm.github.io/data-prep-kit/transforms/language/pdf2parquet/python/)

### Document chunking
- 💻 [Doc Chunking GitHub](https://github.com/IBM/data-prep-kit/tree/dev/transforms/language/doc_chunk)
- 📖 [Doc Chunking docs](https://ibm.github.io/data-prep-kit/transforms/language/doc_chunk/python/)

```
</content>
</file_45>

<file_46>
<path>integrations/docetl.md</path>
<content>
```markdown
Docling is available as a file conversion method in [DocETL](https://github.com/ucbepic/docetl):

- 💻 [DocETL GitHub][github]
- 📖 [DocETL docs][docs]
- 📦 [DocETL PyPI][pypi]

[github]: https://github.com/ucbepic/docetl
[docs]: https://ucbepic.github.io/docetl/
[pypi]: https://pypi.org/project/docetl/

```
</content>
</file_46>

<file_47>
<path>integrations/haystack.md</path>
<content>
```markdown
Docling is available as a converter in [Haystack](https://haystack.deepset.ai/):

- 📖 [Docling Haystack integration docs][docs]
- 💻 [Docling Haystack integration GitHub][github]
- 🧑🏽‍🍳 [Docling Haystack integration example][example]
- 📦 [Docling Haystack integration PyPI][pypi]

[github]: https://github.com/DS4SD/docling-haystack
[docs]: https://haystack.deepset.ai/integrations/docling
[pypi]: https://pypi.org/project/docling-haystack
[example]: ../examples/rag_haystack.ipynb

```
</content>
</file_47>

<file_48>
<path>integrations/index.md</path>
<content>
```markdown
Use the navigation on the left to browse through Docling integrations with popular frameworks and tools.


<p align="center">
  <img loading="lazy" alt="Docling" src="../assets/docling_ecosystem.png" width="100%" />
</p>

```
</content>
</file_48>

<file_49>
<path>integrations/instructlab.md</path>
<content>
```markdown
Docling is powering document processing in [InstructLab][home],
enabling users to unlock the knowledge hidden in documents and present it to
InstructLab's fine-tuning for aligning AI models to the user's specific data.

More details can be found in this [blog post][blog].

- 🏠 [InstructLab home][home]
- 💻 [InstructLab GitHub][github]
- 🧑🏻‍💻 [InstructLab UI][ui]
- 📖 [InstructLab docs][docs]

[home]: https://instructlab.ai
[github]: https://github.com/instructlab
[ui]: https://ui.instructlab.ai/
[docs]: https://docs.instructlab.ai/
[blog]: https://www.redhat.com/en/blog/docling-missing-document-processing-companion-generative-ai

```
</content>
</file_49>

<file_50>
<path>integrations/kotaemon.md</path>
<content>
```markdown
Docling is available in [Kotaemon](https://cinnamon.github.io/kotaemon/) as the `DoclingReader` loader:

- 💻 [Kotaemon GitHub][github]
- 📖 [DoclingReader docs][docs]
- ⚙️ [Docling setup in Kotaemon][setup]

[github]: https://github.com/Cinnamon/kotaemon
[docs]: https://cinnamon.github.io/kotaemon/reference/loaders/docling_loader/
[setup]: https://cinnamon.github.io/kotaemon/development/?h=docling#setup-multimodal-document-parsing-ocr-table-parsing-figure-extraction

```
</content>
</file_50>

<file_51>
<path>integrations/langchain.md</path>
<content>
```markdown
Docling is available as an official [LangChain](https://python.langchain.com/) extension.

To get started, check out the [step-by-step guide in LangChain][guide].

- 📖 [LangChain Docling integration docs][docs]
- 💻 [LangChain Docling integration GitHub][github]
- 🧑🏽‍🍳 [LangChain Docling integration example][example]
- 📦 [LangChain Docling integration PyPI][pypi]

[docs]: https://python.langchain.com/docs/integrations/providers/docling/
[github]: https://github.com/DS4SD/docling-langchain
[guide]: https://python.langchain.com/docs/integrations/document_loaders/docling/
[example]: ../examples/rag_langchain.ipynb
[pypi]: https://pypi.org/project/langchain-docling/

```
</content>
</file_51>

<file_52>
<path>integrations/llamaindex.md</path>
<content>
```markdown
Docling is available as an official [LlamaIndex](https://docs.llamaindex.ai/) extension.

To get started, check out the [step-by-step guide in LlamaIndex](https://docs.llamaindex.ai/en/stable/examples/data_connectors/DoclingReaderDemo/).

## Components

### Docling Reader

Reads document files and uses Docling to populate LlamaIndex `Document` objects — either serializing Docling's data model (losslessly, e.g. as JSON) or exporting to a simplified format (lossily, e.g. as Markdown).

- 💻 [Docling Reader GitHub](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/readers/llama-index-readers-docling)
- 📖 [Docling Reader docs](https://docs.llamaindex.ai/en/stable/api_reference/readers/docling/)
- 📦 [Docling Reader PyPI](https://pypi.org/project/llama-index-readers-docling/)

### Docling Node Parser

Reads LlamaIndex `Document` objects populated in Docling's format by Docling Reader and, using its knowledge of the Docling format, parses them to LlamaIndex `Node` objects for downstream usage in LlamaIndex applications, e.g. as chunks for embedding.

- 💻 [Docling Node Parser GitHub](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/node_parser/llama-index-node-parser-docling)
- 📖 [Docling Node Parser docs](https://docs.llamaindex.ai/en/stable/api_reference/node_parser/docling/)
- 📦 [Docling Node Parser PyPI](https://pypi.org/project/llama-index-node-parser-docling/)

```
</content>
</file_52>

<file_53>
<path>integrations/nvidia.md</path>
<content>
```markdown
Docling is powering the NVIDIA *PDF to Podcast* agentic AI blueprint:

- [🏠 PDF to Podcast home](https://build.nvidia.com/nvidia/pdf-to-podcast)
- [💻 PDF to Podcast GitHub](https://github.com/NVIDIA-AI-Blueprints/pdf-to-podcast)
- [📣 PDF to Podcast announcement](https://nvidianews.nvidia.com/news/nvidia-launches-ai-foundation-models-for-rtx-ai-pcs)
- [✍️ PDF to Podcast blog post](https://blogs.nvidia.com/blog/agentic-ai-blueprints/)

```
</content>
</file_53>

<file_54>
<path>integrations/opencontracts.md</path>
<content>
```markdown
Docling is available an ingestion engine for [OpenContracts](https://github.com/JSv4/OpenContracts), allowing you to use Docling's OCR engine(s), chunker(s), labels, etc. and load them into a platform supporting bulk data extraction, text annotating, and question-answering:

- 💻 [OpenContracts GitHub](https://github.com/JSv4/OpenContracts)
- 📖 [OpenContracts Docs](https://jsv4.github.io/OpenContracts/)
- ▶️ [OpenContracts x Docling PDF annotation screen capture](https://github.com/JSv4/OpenContracts/blob/main/docs/assets/images/gifs/PDF%20Annotation%20Flow.gif)

```
</content>
</file_54>

<file_55>
<path>integrations/prodigy.md</path>
<content>
```markdown
Docling is available in [Prodigy][home] as a [Prodigy-PDF plugin][plugin] recipe.

More details can be found in this [blog post][blog].

- 🌐 [Prodigy home][home]
- 🔌 [Prodigy-PDF plugin][plugin]
- 🧑🏽‍🍳 [pdf-spans.manual recipe][recipe]

[home]: https://prodi.gy/
[plugin]: https://prodi.gy/docs/plugins#pdf
[recipe]: https://prodi.gy/docs/plugins#pdf-spans.manual
[blog]: https://explosion.ai/blog/pdfs-nlp-structured-data

```
</content>
</file_55>

<file_56>
<path>integrations/rhel_ai.md</path>
<content>
```markdown
Docling is powering document processing in [Red Hat Enterprise Linux AI (RHEL AI)](https://rhel.ai),
enabling users to unlock the knowledge hidden in documents and present it to
InstructLab's fine-tuning for aligning AI models to the user's specific data.

- 📣 [RHEL AI 1.3 announcement](https://www.redhat.com/en/about/press-releases/red-hat-delivers-next-wave-gen-ai-innovation-new-red-hat-enterprise-linux-ai-capabilities)
- ✍️ RHEL blog posts:
    - [RHEL AI 1.3 Docling context aware chunking: What you need to know](https://www.redhat.com/en/blog/rhel-13-docling-context-aware-chunking-what-you-need-know)
    - [Docling: The missing document processing companion for generative AI](https://www.redhat.com/en/blog/docling-missing-document-processing-companion-generative-ai)

```
</content>
</file_56>

<file_57>
<path>integrations/spacy.md</path>
<content>
```markdown
Docling is available in [spaCy](https://spacy.io/) as the *spaCy Layout* plugin.

More details can be found in this [blog post][blog].

- 💻 [SpacyLayout GitHub][github]
- 📖 [SpacyLayout docs][docs]
- 📦 [SpacyLayout PyPI][pypi]

[github]: https://github.com/explosion/spacy-layout
[docs]: https://github.com/explosion/spacy-layout?tab=readme-ov-file#readme
[pypi]: https://pypi.org/project/spacy-layout/
[blog]: https://explosion.ai/blog/pdfs-nlp-structured-data

```
</content>
</file_57>

<file_58>
<path>integrations/txtai.md</path>
<content>
```markdown
Docling is available as a text extraction backend for [txtai](https://neuml.github.io/txtai/).

- 💻 [txtai GitHub][github]
- 📖 [txtai docs][docs]
- 📖 [txtai Docling backend][integration_docs]

[github]: https://github.com/neuml/txtai
[docs]: https://neuml.github.io/txtai
[integration_docs]: https://neuml.github.io/txtai/pipeline/data/filetohtml/#docling

```
</content>
</file_58>

<file_59>
<path>integrations/vectara.md</path>
<content>
```markdown
Docling is available as a document parser in [Vectara](https://www.vectara.com/).

- 💻 [Vectara GitHub org](https://github.com/vectara)
    - [vectara-ingest GitHub repo](https://github.com/vectara/vectara-ingest)
- 📖 [Vectara docs](https://docs.vectara.com/)

```
</content>
</file_59>

<file_60>
<path>overrides/main.html</path>
<content>
```html
{% extends "base.html" %}

{#
{% block announce %}
  <p>🎉 Docling has gone v2! <a href="{{ 'v2' | url }}">Check out</a> what's new and how to get started!</p>
{% endblock %}
#}

```
</content>
</file_60>

<file_61>
<path>reference/cli.md</path>
<content>
```markdown
# CLI reference

This page provides documentation for our command line tools.

::: mkdocs-click
    :module: docling.cli.main
    :command: click_app
    :prog_name: docling
    :style: table

```
</content>
</file_61>

<file_62>
<path>reference/docling_document.md</path>
<content>
```markdown
# Docling Document

This is an automatic generated API reference of the DoclingDocument type.

::: docling_core.types.doc
    handler: python
    options:
        members:
            - DoclingDocument
            - DocumentOrigin
            - DocItem
            - DocItemLabel
            - ProvenanceItem
            - GroupItem
            - GroupLabel
            - NodeItem
            - PageItem
            - FloatingItem
            - TextItem
            - TableItem
            - TableCell
            - TableData
            - TableCellLabel
            - KeyValueItem
            - SectionHeaderItem
            - PictureItem
            - ImageRef
            - PictureClassificationClass
            - PictureClassificationData
            - RefItem
            - BoundingBox
            - CoordOrigin
            - ImageRefMode
            - Size
        docstring_style: sphinx
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_"]
        heading_level: 2
        show_root_toc_entry: true
        inherited_members: true
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        show_labels: false
        signature_crossrefs: true
        summary: true

```
</content>
</file_62>

<file_63>
<path>reference/document_converter.md</path>
<content>
```markdown
# Document converter

This is an automatic generated API reference of the main components of Docling.

::: docling.document_converter
    handler: python
    options:
        members:
            - DocumentConverter
            - ConversionResult
            - ConversionStatus
            - FormatOption
            - InputFormat
            - PdfFormatOption
            - ImageFormatOption
            - StandardPdfPipeline
            - WordFormatOption
            - PowerpointFormatOption
            - MarkdownFormatOption
            - AsciiDocFormatOption
            - HTMLFormatOption
            - SimplePipeline
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_"]
        heading_level: 2
        inherited_members: true
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        signature_crossrefs: true
        summary: true

```
</content>
</file_63>

<file_64>
<path>reference/pipeline_options.md</path>
<content>
```markdown
# Pipeline options

Pipeline options allow to customize the execution of the models during the conversion pipeline.
This includes options for the OCR engines, the table model as well as enrichment options which
can be enabled with `do_xyz = True`.


This is an automatic generated API reference of the all the pipeline options available in Docling.


::: docling.datamodel.pipeline_options
    handler: python
    options:
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_"]
        heading_level: 2
        inherited_members: true
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        signature_crossrefs: true
        summary: true

<!-- ::: docling.document_converter.DocumentConverter
    handler: python
    options:
        show_if_no_docstring: true
        show_submodules: true -->
        

```
</content>
</file_64>

<file_65>
<path>stylesheets/extra.css</path>
<content>
```css
[data-md-color-scheme="default"] .md-banner a {
    color: #5e8bde;
}

```
</content>
</file_65>

<file_66>
<path>supported_formats.md</path>
<content>
```markdown
Docling can parse various documents formats into a unified representation (Docling
Document), which it can export to different formats too — check out
[Architecture](./concepts/architecture.md) for more details.

Below you can find a listing of all supported input and output formats.

## Supported input formats

| Format | Description |
|--------|-------------|
| PDF | |
| DOCX, XLSX, PPTX | Default formats in MS Office 2007+, based on Office Open XML |
| Markdown | |
| AsciiDoc | |
| HTML, XHTML | |
| PNG, JPEG, TIFF, BMP | Image formats |

Schema-specific support:

| Format | Description |
|--------|-------------|
| USPTO XML | XML format followed by [USPTO](https://www.uspto.gov/patents) patents |
| PMC XML | XML format followed by [PubMed Central®](https://pmc.ncbi.nlm.nih.gov/) articles |
| Docling JSON | JSON-serialized [Docling Document](./concepts/docling_document.md) |

## Supported output formats

| Format | Description |
|--------|-------------|
| HTML | Both image embedding and referencing are supported |
| Markdown | |
| JSON | Lossless serialization of Docling Document |
| Text | Plain text, i.e. without Markdown markers |
| Doctags | |

```
</content>
</file_66>

<file_67>
<path>usage.md</path>
<content>
```markdown
## Conversion

### Convert a single document

To convert individual PDF documents, use `convert()`, for example:

```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # PDF path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "### Docling Technical Report[...]"
```

### CLI

You can also use Docling directly from your command line to convert individual files —be it local or by URL— or whole directories.

A simple example would look like this:
```console
docling https://arxiv.org/pdf/2206.01062
```

To see all available options (export formats etc.) run `docling --help`. More details in the [CLI reference page](./reference/cli.md).

### Advanced options

#### Adjust pipeline features

The example file [custom_convert.py](./examples/custom_convert.py) contains multiple ways
one can adjust the conversion pipeline and features.


##### Control PDF table extraction options

You can control if table structure recognition should map the recognized structure back to PDF cells (default) or use text cells from the structure prediction itself.
This can improve output quality if you find that multiple columns in extracted tables are erroneously merged into one.


```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False  # uses text cells predicted from table structure model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

Since docling 1.16.0: You can control which TableFormer mode you want to use. Choose between `TableFormerMode.FAST` (default) and `TableFormerMode.ACCURATE` (better, but slower) to receive better quality with difficult table structures.

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # use more accurate TableFormer model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

##### Provide specific artifacts path

By default, artifacts such as models are downloaded automatically upon first usage. If you would prefer to use a local path where the artifacts have been explicitly prefetched, you can do that as follows:

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

# # to explicitly prefetch:
# artifacts_path = StandardPdfPipeline.download_models_hf()

artifacts_path = "/local/path/to/artifacts"

pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

#### Impose limits on the document size

You can limit the file size and number of pages which should be allowed to process per document:

```python
from pathlib import Path
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"
converter = DocumentConverter()
result = converter.convert(source, max_num_pages=100, max_file_size=20971520)
```

#### Convert from binary PDF streams

You can convert PDFs from a binary stream instead of from the filesystem as follows:

```python
from io import BytesIO
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

buf = BytesIO(your_binary_stream)
source = DocumentStream(name="my_doc.pdf", stream=buf)
converter = DocumentConverter()
result = converter.convert(source)
```

#### Limit resource usage

You can limit the CPU threads used by Docling by setting the environment variable `OMP_NUM_THREADS` accordingly. The default setting is using 4 CPU threads.


#### Use specific backend converters

!!! note

    This section discusses directly invoking a [backend](./concepts/architecture.md),
    i.e. using a low-level API. This should only be done when necessary. For most cases,
    using a `DocumentConverter` (high-level API) as discussed in the sections above
    should suffice — and is the recommended way.

By default, Docling will try to identify the document format to apply the appropriate conversion backend (see the list of [supported formats](./supported_formats.md)).
You can restrict the `DocumentConverter` to a set of allowed document formats, as shown in the [Multi-format conversion](./examples/run_with_formats.py) example.
Alternatively, you can also use the specific backend that matches your document content. For instance, you can use `HTMLDocumentBackend` for HTML pages:

```python
import urllib.request
from io import BytesIO
from docling.backend.html_backend import HTMLDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

url = "https://en.wikipedia.org/wiki/Duck"
text = urllib.request.urlopen(url).read()
in_doc = InputDocument(
    path_or_stream=BytesIO(text),
    format=InputFormat.HTML,
    backend=HTMLDocumentBackend,
    filename="duck.html",
)
backend = HTMLDocumentBackend(in_doc=in_doc, path_or_stream=BytesIO(text))
dl_doc = backend.convert()
print(dl_doc.export_to_markdown())
```

## Chunking

You can chunk a Docling document using a [chunker](concepts/chunking.md), such as a
`HybridChunker`, as shown below (for more details check out
[this example](examples/hybrid_chunking.ipynb)):

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

conv_res = DocumentConverter().convert("https://arxiv.org/pdf/2206.01062")
doc = conv_res.document

chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5")  # set tokenizer as needed
chunk_iter = chunker.chunk(doc)
```

An example chunk would look like this:

```python
print(list(chunk_iter)[11])
# {
#   "text": "In this paper, we present the DocLayNet dataset. [...]",
#   "meta": {
#     "doc_items": [{
#       "self_ref": "#/texts/28",
#       "label": "text",
#       "prov": [{
#         "page_no": 2,
#         "bbox": {"l": 53.29, "t": 287.14, "r": 295.56, "b": 212.37, ...},
#       }], ...,
#     }, ...],
#     "headings": ["1 INTRODUCTION"],
#   }
# }
```

```
</content>
</file_67>

<file_68>
<path>v2.md</path>
<content>
```markdown
## What's new

Docling v2 introduces several new features:

- Understands and converts PDF, MS Word, MS Powerpoint, HTML and several image formats
- Produces a new, universal document representation which can encapsulate document hierarchy
- Comes with a fresh new API and CLI

## Changes in Docling v2

### CLI

We updated the command line syntax of Docling v2 to support many formats. Examples are seen below.
```shell
# Convert a single file to Markdown (default)
docling myfile.pdf

# Convert a single file to Markdown and JSON, without OCR
docling myfile.pdf --to json --to md --no-ocr

# Convert PDF files in input directory to Markdown (default)
docling ./input/dir --from pdf

# Convert PDF and Word files in input directory to Markdown and JSON
docling ./input/dir --from pdf --from docx --to md --to json --output ./scratch

# Convert all supported files in input directory to Markdown, but abort on first error
docling ./input/dir --output ./scratch --abort-on-error

```

**Notable changes from Docling v1:**

- The standalone switches for different export formats are removed, and replaced with `--from` and `--to` arguments, to define input and output formats respectively.
- The new `--abort-on-error` will abort any batch conversion as soon an error is encountered
- The `--backend` option for PDFs was removed

### Setting up a `DocumentConverter`

To accomodate many input formats, we changed the way you need to set up your `DocumentConverter` object.
You can now define a list of allowed formats on the `DocumentConverter` initialization, and specify custom options
per-format if desired. By default, all supported formats are allowed. If you don't provide `format_options`, defaults
will be used for all `allowed_formats`.

Format options can include the pipeline class to use, the options to provide to the pipeline, and the document backend.
They are provided as format-specific types, such as `PdfFormatOption` or `WordFormatOption`, as seen below.

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

## Default initialization still works as before:
# doc_converter = DocumentConverter()


# previous `PipelineOptions` is now `PdfPipelineOptions`
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = True
#...

## Custom options are now defined per format.
doc_converter = (
    DocumentConverter(  # all of the below is optional, has internal defaults.
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.IMAGE,
            InputFormat.DOCX,
            InputFormat.HTML,
            InputFormat.PPTX,
        ],  # whitelist formats, non-matching files are ignored.
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options, # pipeline options go here.
                backend=PyPdfiumDocumentBackend # optional: pick an alternative backend
            ),
            InputFormat.DOCX: WordFormatOption(
                pipeline_cls=SimplePipeline # default for office formats and HTML
            ),
        },
    )
)
```

**Note**: If you work only with defaults, all remains the same as in Docling v1.

More options are shown in the following example units:

- [run_with_formats.py](examples/run_with_formats.py)
- [custom_convert.py](examples/custom_convert.py)

### Converting documents

We have simplified the way you can feed input to the `DocumentConverter` and renamed the conversion methods for
better semantics. You can now call the conversion directly with a single file, or a list of input files,
or `DocumentStream` objects, without constructing a `DocumentConversionInput` object first.

* `DocumentConverter.convert` now converts a single file input (previously `DocumentConverter.convert_single`).
* `DocumentConverter.convert_all` now converts many files at once (previously `DocumentConverter.convert`).


```python
...
from docling.datamodel.document import ConversionResult
## Convert a single file (from URL or local path)
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Convert several files at once:

input_files = [
    "tests/data/wiki_duck.html",
    "tests/data/word_sample.docx",
    "tests/data/lorem_ipsum.docx",
    "tests/data/powerpoint_sample.pptx",
    "tests/data/2305.03393v1-pg9-img.png",
    "tests/data/2206.01062.pdf",
]

# Directly pass list of files or streams to `convert_all`
conv_results_iter = doc_converter.convert_all(input_files) # previously `convert`

```
Through the `raises_on_error` argument, you can also control if the conversion should raise exceptions when first
encountering a problem, or resiliently convert all files first and reflect errors in each file's conversion status.
By default, any error is immediately raised and the conversion aborts (previously, exceptions were swallowed).

```python
...
conv_results_iter = doc_converter.convert_all(input_files, raises_on_error=False) # previously `convert`

```

### Access document structures

We have simplified how you can access and export the converted document data, too. Our universal document representation
is now available in conversion results as a `DoclingDocument` object.
`DoclingDocument` provides a neat set of APIs to construct, iterate and export content in the document, as shown below.

```python
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Inspect the converted document:
conv_result.document.print_element_tree()

## Iterate the elements in reading order, including hierachy level:
for item, level in conv_result.document.iterate_items():
    if isinstance(item, TextItem):
        print(item.text)
    elif isinstance(item, TableItem):
        table_df: pd.DataFrame = item.export_to_dataframe()
        print(table_df.to_markdown())
    elif ...:
        #...
```

**Note**: While it is deprecated, you can _still_ work with the Docling v1 document representation, it is available as:
```shell
conv_result.legacy_document # provides the representation in previous ExportedCCSDocument type
```

### Export into JSON, Markdown, Doctags
**Note**: All `render_...` methods in `ConversionResult` have been removed in Docling v2,
and are now available on `DoclingDocument` as:

- `DoclingDocument.export_to_dict`
- `DoclingDocument.export_to_markdown`
- `DoclingDocument.export_to_document_tokens`

```python
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Export to desired format:
print(json.dumps(conv_res.document.export_to_dict()))
print(conv_res.document.export_to_markdown())
print(conv_res.document.export_to_document_tokens())
```

**Note**: While it is deprecated, you can _still_ export Docling v1 JSON format. This is available through the same
methods as on the `DoclingDocument` type:
```shell
## Export legacy document representation to desired format, for v1 compatibility:
print(json.dumps(conv_res.legacy_document.export_to_dict()))
print(conv_res.legacy_document.export_to_markdown())
print(conv_res.legacy_document.export_to_document_tokens())
```

### Reload a `DoclingDocument` stored as JSON

You can save and reload a `DoclingDocument` to disk in JSON format using the following codes:

```python
# Save to disk:
doc: DoclingDocument = conv_res.document # produced from conversion result...

with Path("./doc.json").open("w") as fp:
    fp.write(json.dumps(doc.export_to_dict())) # use `export_to_dict` to ensure consistency

# Load from disk:
with Path("./doc.json").open("r") as fp:
    doc_dict = json.loads(fp.read())
    doc = DoclingDocument.model_validate(doc_dict) # use standard pydantic API to populate doc

```

### Chunking

Docling v2 defines new base classes for chunking:

- `BaseMeta` for chunk metadata
- `BaseChunk` containing the chunk text and metadata, and
- `BaseChunker` for chunkers, producing chunks out of a `DoclingDocument`.

Additionally, it provides an updated `HierarchicalChunker` implementation, which
leverages the new `DoclingDocument` and provides a new, richer chunk output format, including:

- the respective doc items for grounding
- any applicable headings for context
- any applicable captions for context

For an example, check out [Chunking usage](usage.md#chunking).

```
</content>
</file_68>
