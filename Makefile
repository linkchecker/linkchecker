# This Makefile is only used by developers.
PAGER ?= less


all:
	@echo "Read the file doc/install.txt to see how to build and install this package."

clean:
	git clean -fdx

locale:
	$(MAKE) -C po

test:
	hatch -e test run tests

upload:
	twine upload dist/LinkChecker*

homepage:
	hatch -e doc run code
	hatch -e doc run html

dist:
	hatchling build

check:
	flake8
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
