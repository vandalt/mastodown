SPHINXOPTS ?=
SPHINXBUILD ?= sphinx-build
PYTHON = python
SOURCEDIR = .
BUILDDIR = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

api:
	@$(PYTHON) generate_api_reference.py

html: api
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" -W $(SPHINXOPTS) $(O)

.PHONY: help api html Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" -W $(SPHINXOPTS) $(O)
