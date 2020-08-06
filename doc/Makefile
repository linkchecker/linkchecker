MANFILES:=linkchecker.1 linkcheckerrc.5
LOCALES:=en de

all:

code: clean
	PYTHONPATH=.. sphinx-autogen src/code/index.rst

html:
	make -C src html

po4a:
	po4a --localized-charset=UTF-8 po4a.conf

# check all makefiles for formatting warnings
check:
	@t=$(shell tempfile); \
	for loc in $(LOCALES); do \
	  for manfile in $(MANFILES); do \
	    echo "Checking $$loc/$$manfile"; \
	    LC_ALL=en_US.UTF-8 MANWIDTH=80 man --warnings -E UTF-8 -l $$loc/$$manfile > /dev/null 2>$$t ; \
	    if [ -s $$t ]; then cat $$t; exit 1; fi; \
	  done; \
	done

clean:
	rm -rf src/_build; \
	rm -rf src/code/linkcheck; \
	rm -rf html

.PHONY: po4a check clean html
