# The whole project's commands. `make build` needs Python 3.9+, PyYAML (pyproject.toml,
# `pip install -e .`) and this checkout: no network, so a clean clone builds offline.

PYTHON ?= python3

.PHONY: build test validate serve clean

build:
	$(PYTHON) bin/build

validate:
	$(PYTHON) bin/validate

# One entry point, and .bureau.yml's test_command: schema validation over data/, then
# the schema and builder tests. Make stops at the first failing line, so either one
# failing fails the target.
test:
	$(PYTHON) bin/validate
	$(PYTHON) -m unittest discover --start-directory tests --top-level-directory .

# For the phone-width check: open http://localhost:8000 at a 375px viewport.
serve: build
	cd site && $(PYTHON) -m http.server 8000

clean:
	rm -rf site
