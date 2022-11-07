# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -W --keep-going
SPHINXBUILD   ?= python3 -m sphinx.cmd.build
SPHINXINTL    ?= python3 -m sphinx_intl.commands
SOURCEDIR     = .
BUILDDIR      = _build
LANGUAGE      = en

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

gettext:
	@$(SPHINXBUILD) -b gettext "$(SOURCEDIR)" -d "$(BUILDDIR)/i18n/doctrees" ../i18n/gettext man/* $(SPHINXOPTS) $(O)

html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" -d "$(BUILDDIR)/doctrees" ../html $(SPHINXOPTS) $(O)

man:
	@$(SPHINXBUILD) -b man "$(SOURCEDIR)" -d "$(BUILDDIR)/doctrees" ../man/$(LANGUAGE) $(SPHINXOPTS) $(O)

locale: gettext
	@$(SPHINXINTL) update -p ../i18n/gettext -l de

.PHONY: help gettext html locale man Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
