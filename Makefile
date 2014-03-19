PACKAGE = comfort-0.1

LANGUES = fr_FR en_US


SOURCES_PY = $(wildcard src/*/*.py)

DIST_FILES = $(SOURCES_PY) \
             debian \
             desktop \
             doc/doc.tex doc/doc.pdf \
             doc/epydoc.conf doc/Makefile doc/README \
             locale \
             Makefile \
             README \
             COPYING \
             AUTHORS \
             src/cgi-bin/images \
             src/index.html \
             src/styles \
             src/templates \
             logo/comfort_icone.png \
             packaging

USER_DIST_FILES = $(SOURCES_PY) \
             doc/doc.pdf \
             locale \
             Makefile \
             README \
             COPYING \
             src/cgi-bin/images \
             src/index.html \
             src/styles \
             src/templates \
             logo/comfort_icone.png


TRAD_FILE = locale/comfort.pot

LANGUES_PO = $(foreach l, $(LANGUES), locale/$l/LC_MESSAGES/comfort.po)
LANGUES_MO = $(foreach l, $(LANGUES), locale/$l/LC_MESSAGES/comfort.mo)

ifndef PREFIX
  PREFIX = /usr
endif
DIR_SRC = $(PREFIX)/share/comfort

.PHONY: all test install uninstall clean dist userdist update dist-update

.PRECIOUS: %.po

all: $(LANGUES_MO)
	echo "Prêt (lancez make test)"

test:
	(cd src/server && ./launch.py)

install:
	# installation de src
	install -d $(DESTDIR)$(DIR_SRC)
	install -m 644 src/index.html $(DESTDIR)$(DIR_SRC)/
	for i in `cd src && ls`; do \
	  if [ -d src/$${i} ]; then \
	    install -d $(DESTDIR)$(DIR_SRC)/$${i}; \
	    case $${i} in \
	    "cgi-bin" | "server") \
	      for j in `cd src && ls $${i}/*.py`; do \
	        install -m 755 src/$${j} $(DESTDIR)$(DIR_SRC)/$${j}; \
	      done;; \
	    "l2p") \
	      install -m 755 src/$${i}/l2p $(DESTDIR)$(DIR_SRC)/$${i}/l2p; \
	      install -m 644 src/$${i}/l2p.html $(DESTDIR)$(DIR_SRC)/$${i}/l2p.html; \
	      install -m 644 src/$${i}/l2p.txt $(DESTDIR)$(DIR_SRC)/$${i}/l2p.txt;; \
	    "styles") \
	      for j in `cd src && find $${i} | grep -v .svn`; do \
	        if [ -d src/$${j} ]; then \
	          install -d $(DESTDIR)$(DIR_SRC)/$${j}; \
	        else \
	          install -m 644 src/$${j} $(DESTDIR)$(DIR_SRC)/$${j}; \
	        fi; \
	      done;; \
	    "templates") \
	      for j in $${i}/fop $${i}/xsl; do \
	        for k in `cd src && find $${j} | grep -v .svn`; do \
	          if [ -d src/$${k} ]; then \
	            install -d $(DESTDIR)$(DIR_SRC)/$${k}; \
	          else \
	            install -m 644 src/$${k} $(DESTDIR)$(DIR_SRC)/$${k}; \
	          fi; \
	        done; \
	      done; \
	      for j in `cd src && ls $${i}/*.py`; do \
	        install -m 644 src/$${j} $(DESTDIR)$(DIR_SRC)/$${j}; \
	      done;; \
	    *) \
	      for j in `cd src && ls $${i}/*.py`; do \
	        install -m 644 src/$${j} $(DESTDIR)$(DIR_SRC)/$${j}; \
	      done;; \
	    esac; \
	  fi; \
	done
	for i in AUTHORS COPYING; do \
	  install -m 644 $${i} $(DESTDIR)$(DIR_SRC)/$${i}; \
	done
	# lien symbolique dans $(PREFIX)/bin
	install -d $(DESTDIR)$(PREFIX)/bin
	ln -sf $(DESTDIR)$(DIR_SRC)/server/launch.py $(DESTDIR)$(PREFIX)/bin/comfort
	# installation de l'entrée desktop
	install -d $(DESTDIR)$(PREFIX)/share/pixmaps
	install -m 644 desktop/comfort.png $(DESTDIR)$(PREFIX)/share/pixmaps/
	install -d $(DESTDIR)$(PREFIX)/share/applications
	install -m 644 desktop/comfort.desktop $(DESTDIR)$(PREFIX)/share/applications/
	# installation de la doc
	install -d $(DESTDIR)$(PREFIX)/share/doc/comfort
	for i in doc/doc*.pdf; do \
	  install -m 644 $${i} $(DESTDIR)$(PREFIX)/share/doc/comfort/; \
	done
	# installation des locales
	for i in `find locale | grep "comfort.mo"`; do \
	  install -m 644 -D $${i} $(DESTDIR)$(PREFIX)/share/$${i}; \
	done

uninstall:
	rm -rf $(DESTDIR)$(DIR_SRC)
	rm -f $(DESTDIR)$(PREFIX)/bin/comfort
	rm -f $(DESTDIR)$(PREFIX)/share/pixmaps/comfort.png
	rm -f $(DESTDIR)$(PREFIX)/share/applications/comfort.desktop
	rm -rf $(DESTDIR)$(PREFIX)/share/doc/comfort
	rm -f `find $(DESTDIR)$(PREFIX)/share/locale | grep "comfort.mo"`

dist: $(LANGUES_MO)
	cd .. && mv CONFORT $(PACKAGE) && tar cvzf $(PACKAGE).tar.gz  \
		--exclude=*.pyc \
		--exclude=*~ \
		--exclude=.svn \
		--exclude=$(PACKAGE)/src/conf/conf.py \
		--exclude=$(PACKAGE)/src/conf/conf_private.py \
		--exclude=$(PACKAGE)/src/latex/*/*.png \
		$(foreach d, $(DIST_FILES), $(PACKAGE)/$d) && mv $(PACKAGE) CONFORT
	echo "Archive créée dans '$(PWD)/..'."

userdist: $(LANGUES_MO)
	cd .. && mv CONFORT $(PACKAGE) && tar cvzf $(PACKAGE).tar.gz  \
		--exclude=*.pyc \
		--exclude=*~ \
		--exclude=.svn \
		--exclude=$(PACKAGE)/src/conf/conf.py \
		--exclude=$(PACKAGE)/src/conf/conf_private.py \
		$(foreach d, $(USER_DIST_FILES), $(PACKAGE)/$d) && mv $(PACKAGE) CONFORT
	@echo "Archive créée dans `dirname "$(PWD)" `"

update:
	svn update

dist-update: update dist

$(TRAD_FILE): $(SOURCES_PY)
	xgettext -k_ $(SOURCES_PY) -o $(TRAD_FILE)

%.po: $(TRAD_FILE)
	mkdir -p $(@:.po=)
	rmdir $(@:.po=)
	test -e $@ || msginit -i $(TRAD_FILE) -o $@ --no-translator
	msgmerge -U $@ $(TRAD_FILE)

%.mo: %.po
	msgfmt -o $@ $<

clean:
	rm -rf `find . -iname '*.pyc'`
	rm -rf `find . -iname '*~'`
