#### Python Environment ####
.PHONY: install
install: 
	pip install -r ./requirements.txt
	pip install -r ./requirements-dev.txt

.PHONY: uninstall
uninstall:
	@bash -c "pip uninstall -y -r <(pip freeze)"

#### Development ####
.PHONY: jupyter
jupyter: 
	@jupyter lab --autoreload --no-browser



#### LLM Context ####
FILETREE_SCRIPT=./llm/file_tree.py
FILETREE_SRC=./llm/context/src_tree.md
FILETREE_DOCS=./llm/context/docs_tree.md
FILETREE_UNITTEST=./llm/context/unittest_tree.md

CONTENT_SCRIPT=./llm/file_tree_to_markdown.py
CONTENT_SRC=./llm/context/src_content.md
CONTENT_DOCS=./llm/context/docs_content.md
CONTENT_UNITTEST=./llm/context/unittest_content.md

.PHONY: context
context: context.src context.unittest context.docs

# --- SRC directory
.PHONY: context.src
context.src:filetree.src content.src

.PHONY: filetree.src
filetree.src:
	@python $(FILETREE_SCRIPT) \
		--directory ./src \
		--level 10 \
		--exclude-suffixes .pyc .pyo .pyd \
		--exclude-filenames __pycache__ .git .pytest_cache .env .venv node_modules .ipynb_checkpoints\
		--include-base-path \
		-o $(FILETREE_SRC)

.PHONY: content.src
content.src:
	@python $(CONTENT_SCRIPT) $(FILETREE_SRC) -o $(CONTENT_SRC)

# --- DOCS directory
.PHONY: context.docs
context.docs:filetree.docs content.docs

.PHONY: filetree.docs
filetree.docs:
	@python $(FILETREE_SCRIPT) \
		--directory ./docs \
		--level 10 \
		--exclude-suffixes .pyc .pyo .pyd \
		--exclude-filenames __pycache__ .git .pytest_cache .env .venv node_modules .ipynb_checkpoints data\
		--include-base-path \
		-o $(FILETREE_DOCS)

.PHONY: content.docs
content.docs:
	@python $(CONTENT_SCRIPT) $(FILETREE_DOCS) -o $(CONTENT_DOCS)

# --- UNITTEST directory
.PHONY: context.unittest
context.unittest:filetree.unittest content.unittest

.PHONY: filetree.unittest
filetree.unittest:
	@python $(FILETREE_SCRIPT) \
		--directory ./tests \
		--level 10 \
		--exclude-suffixes .pyc .pyo .pyd \
		--exclude-filenames __pycache__ .git .pytest_cache .env .venv node_modules .ipynb_checkpoints\
		--include-base-path \
		-o $(FILETREE_UNITTEST)

.PHONY: content.unittest
content.unittest:
	@python $(CONTENT_SCRIPT) $(FILETREE_UNITTEST) -o $(CONTENT_UNITTEST)