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


