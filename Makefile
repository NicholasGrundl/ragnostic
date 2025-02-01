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
FILETREE_SRC=./llm/context/src_tree.md
FILETREE_REPO=./llm/context/repo_tree.md
CONTENT_SCRIPT=./llm/file_tree_to_markdown.py
CONTENT_SRC=./llm/context/src_content.md
CONTENT_REPO=./llm/context/repo_content.md

.PHONY: context
context: context.src

.PHONY: context.src
context.src:filetree.src content.src

.PHONY: context.repo
context.repo:filetree.repo content.repo

.PHONY: filetree.src
filetree.src:
	@python $(FILETREE_SCRIPT) \
		--directory ./src \
		--level 10 \
		--exclude-suffixes .pyc .pyo .pyd \
		--exclude-filenames __pycache__ .git .pytest_cache .env .venv node_modules .ipynb_checkpoints\
		--include-base-path \
		-o $(FILETREE_SRC)


.PHONY: filetree.repo
filetree.repo:
	@python $(FILETREE_SCRIPT) \
		--directory . \
		--level 10 \
		--exclude-suffixes .pyc .pyo .pyd \
		--exclude-filenames __pycache__ .git .pytest_cache .env .venv node_modules .ipynb_checkpoints data\
		--include-base-path \
		-o $(FILETREE_REPO)


.PHONY: content.src
content.src:
	@python $(CONTENT_SCRIPT) $(FILETREE_SRC) -o $(CONTENT_SRC)

.PHONY: content.repo
content.repo:
	@python $(CONTENT_SCRIPT) $(FILETREE_REPO) -o $(CONTENT_REPO)