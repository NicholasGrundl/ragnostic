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



FILETREE_SCRIPT=./llm/file_tree.py
FILETREE_OUTPUT=./llm/tree.md
SOURCE_SCRIPT=./llm/file_tree_to_markdown.py
SOURCE_OUTPUT=./llm/tree_source.md
.PHONY: filetree
filetree:filetree.src

.PHONY: filetree.src
filetree.src:
	@python $(FILETREE_SCRIPT) \
		--directory ./src \
		--level 10 \
		--exclude-suffixes .pyc .pyo .pyd \
		--exclude-filenames __pycache__ .git .pytest_cache .env .venv node_modules .ipynb_checkpoints\
		--include-base-path \
	| tee $(FILETREE_OUTPUT)

.PHONY: filetree.repo
filetree.repo:
	@python $(FILETREE_SCRIPT) \
		--directory . \
		--level 10 \
		--exclude-suffixes .pyc .pyo .pyd \
		--exclude-filenames __pycache__ .git .pytest_cache .env .venv node_modules .ipynb_checkpoints data\
		--include-base-path \
	| tee $(FILETREE_OUTPUT)

.PHONY: source
source:
	@python $(SOURCE_SCRIPT) $(FILETREE_OUTPUT) -o $(SOURCE_OUTPUT)
