# Background

This folder contains some prompts, scripts and other utilities used to help me code with LLMs.



# Repo Context

To feed context for a specific package you want to use follow these steps:

1. Clone the repo to a <repo_location>

2. run the file tree on the docs and src code
```bash
python ./llm/file_tree.py --directory <docs_subfolder> --level 10 --exclude-suffixes .pyc .pyo .pyd --include-base-path -o <context_tree_filepath>
```

3. Generate the markdown of the file tree
```bash
python ./llm/file_tree_to_markdown.py <docs_subfolder> -o <context_content_filepath>
```