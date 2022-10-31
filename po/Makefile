XGETTEXT := xgettext
MSGFMT := msgfmt
MSGMERGE := msgmerge
POSOURCES = $(shell find ../linkcheck -name \*.py) \
	$(shell python3 -c 'import argparse; print(argparse.__file__)')
PACKAGE = linkchecker
TEMPLATE = $(PACKAGE).pot
MYMAIL := bastian.kleineidam@web.de
BUGSURL = https://github.com/linkchecker/linkchecker
POFILES = $(wildcard *.po)

all:	$(POFILES)

%.po:	$(TEMPLATE)
	$(MSGMERGE) -U --suffix=.bak $@ $<

template: $(TEMPLATE)
$(TEMPLATE): $(POSOURCES)
	$(XGETTEXT) -w 80 --default-domain=$(PACKAGE) --language=Python \
	  --copyright-holder="Bastian Kleineidam <$(MYMAIL)>" \
	  --package-name=LinkChecker \
	  --from-code=UTF-8 \
	  --msgid-bugs-address=$(BUGSURL) -o $(TEMPLATE) \
	  --keyword=_n:1,2 $(POSOURCES)

check:
	@for po in $(POFILES); do \
		$(MSGFMT) -cv --statistics -o - $$po >/dev/null; \
	done

clean:
	rm -f *.bak

.PHONY: check clean
