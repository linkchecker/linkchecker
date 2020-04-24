HTMLDIR:=web/media
MANHTMLFILES:= \
	$(HTMLDIR)/man1/linkchecker.1.html \
	$(HTMLDIR)/man5/linkcheckerrc.5.html

MANFILES:=linkchecker.1 linkcheckerrc.5
LOCALES:=en de

all:

po4a:
	po4a --localized-charset=UTF-8 po4a.conf

man:	$(MANHTMLFILES)

$(HTMLDIR)/man1/linkchecker.1.html: en/linkchecker.1
	mandoc -Thtml $< > $@
	@sed -i -e \
	  's:<b>linkcheckerrc</b>(5):<a href="../man5/linkcheckerrc.5.html" class="Xr">linkcheckerrc(5)</a>:g' \
	  $(HTMLDIR)/man1/linkchecker.1.html

$(HTMLDIR)/man5/linkcheckerrc.5.html: en/linkcheckerrc.5
	mandoc -Thtml $< > $@
	@sed -i -e \
	  's:<b>linkchecker</b>(1):<a href="../man1/linkchecker.1.html" class="Xr">linkchecker(1)</a>:g' \
	  $(HTMLDIR)/man5/linkcheckerrc.5.html

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
	rm $(MANHTMLFILES)

.PHONY: po4a man check clean

