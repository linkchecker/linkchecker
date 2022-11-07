MANFILES:=linkchecker.1 linkcheckerrc.5
LOCALES:=en de

all: html man

html: clean
	make -C src html

locale:
	make -C src locale

man:
	make -C src man; \
	make -C src -e SPHINXOPTS="-D language='de' -t de" LANGUAGE="de" man

# check all man files for formatting warnings
check:
	@for loc in $(LOCALES); do \
	  for manfile in $(MANFILES); do \
	    echo "Checking man/$$loc/$$manfile"; \
	    LC_ALL=en_US.UTF-8 MANWIDTH=80 mandoc -T lint -W error man/$$loc/$$manfile; \
	  done; \
	done

clean:
	rm -rf src/_build; \
	rm -rf src/code/linkcheck; \
	rm -rf html

.PHONY: check clean html locale man
