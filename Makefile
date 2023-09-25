# This Makefile is only used by developers.
PAGER ?= less


all:
	@echo "Read the file doc/install.txt to see how to build and install this package."

clean:
	git clean -fdx

locale:
	$(MAKE) -C po

linkcheck/_release.py:
	hatchling build -t sdist --hooks-only

test: linkcheck/_release.py
	tox -e py

upload:
	twine upload dist/LinkChecker*

homepage: linkcheck/_release.py
	make -C doc html

dist:
	hatchling build

check:
	flake8
	yamllint .github
	make -C doc check
	make -C po check

releasecheck: check
	@if egrep -i "xx\.|xxxx|\.xx|^[[:digit:]]+\.x" doc/changelog.txt > /dev/null; then \
	  echo "Could not release: edit doc/changelog.txt release date"; false; \
	fi

count:
	@sloccount linkcheck tests


.PHONY: test count upload all clean
.PHONY: locale dist homepage
