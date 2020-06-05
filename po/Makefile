XGETTEXT := xgettext
MSGFMT := msgfmt
MSGMERGE := msgmerge
POSOURCES = $(shell find ../linkcheck -name \*.py) \
	../linkchecker $(shell python3 -c 'import argparse; print(argparse.__file__)')
LDIR = ../share/locale
PACKAGE = linkchecker
TEMPLATE = $(PACKAGE).pot
MYMAIL := bastian.kleineidam@web.de
LFILE = LC_MESSAGES/$(PACKAGE).mo
# defined language (add new languages here)
LANGUAGES = de fr es
MOFILES = $(wildcard *.mo)

all:	$(MOFILES)

%.mo:	%.po
	$(MSGFMT) -c --statistics -o $@ $<

%.po:	$(TEMPLATE)
	$(MSGMERGE) -U --suffix=.bak $@ $<

template: $(TEMPLATE)
$(TEMPLATE): $(POSOURCES)
	$(XGETTEXT) -w 80 --default-domain=$(PACKAGE) --language=Python \
	  --copyright-holder="Bastian Kleineidam <$(MYMAIL)>" \
	  --msgid-bugs-address=$(MYMAIL) -o $(TEMPLATE) \
	  --keyword=_n:1,2 $(POSOURCES)

clean:
	@for f in $(LANGUAGES); do rm -f $(LDIR)/$$f/$(LFILE); done
	rm -f *.mo *.bak

.PHONY: clean
