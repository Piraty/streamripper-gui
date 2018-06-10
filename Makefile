export SHELL = sh
PACKAGE = streamripper-gui
VERSION = 0.1.2
COPYRIGHTYEAR = 2012
AUTHOR = Krasimir S. Stefanov (lokster)
EMAIL = lokiisyourmaster@gmail.com

all: debian

debian: translations
	[ ! -d ./build/debian/ ] || rm -r ./build/debian/
	sed -i 's/APP_VERSION = ".*"/APP_VERSION = "'$(VERSION)'"/' src/streamripper-gui.py
	mkdir -p ./build/debian/usr/bin
	mkdir -p ./build/debian/usr/share/applications/
	mkdir -p ./build/debian/usr/share/streamripper-gui/
	mkdir -p ./dist
	
	cp src/streamripper-gui.desktop ./build/debian/usr/share/applications/
	cp src/*.py ./build/debian/usr/share/streamripper-gui/
# 	cp src/*.png ./build/debian/usr/share/streamripper-gui/
	cp src/streamripper-gui.glade ./build/debian/usr/share/streamripper-gui/
	cp src/streamripper-gui ./build/debian/usr/bin/
	
	cp -r locale ./build/debian/usr/share
	
	./tools/debian-package.sh "$(PACKAGE)" "$(VERSION)" "$(AUTHOR)" "$(EMAIL)"
	
pot:
	[ -d ./po/ ] || mkdir ./po
	xgettext --default-domain="$(PACKAGE)" --output="po/$(PACKAGE).pot" src/*.py src/*.glade
	sed -i 's/SOME DESCRIPTIVE TITLE/Translation template for $(PACKAGE)/' po/$(PACKAGE).pot
	sed -i "s/YEAR THE PACKAGE'S COPYRIGHT HOLDER/$(COPYRIGHTYEAR)/" po/$(PACKAGE).pot
	sed -i 's/FIRST AUTHOR <EMAIL@ADDRESS>, YEAR/$(AUTHOR) <$(EMAIL)>, $(COPYRIGHTYEAR)/' po/$(PACKAGE).pot
	sed -i 's/Report-Msgid-Bugs-To: /Report-Msgid-Bugs-To: $(EMAIL)/' po/$(PACKAGE).pot
	sed -i 's/CHARSET/UTF-8/' po/$(PACKAGE).pot
	sed -i 's/PACKAGE VERSION/$(VERSION)/' po/$(PACKAGE).pot
	sed -i 's/PACKAGE/$(PACKAGE)/' po/$(PACKAGE).pot

update-po: pot
	for i in po/*.po ;\
	do \
	mv $$i $${i}.old ; \
	(msgmerge $${i}.old po/$(PACKAGE).pot | msgattrib --no-obsolete > $$i) ; \
	rm $${i}.old ; \
	done

translations: po/*.po
	mkdir -p locale
	@for po in $^; do \
		language=`basename $$po`; \
		language=$${language%%.po}; \
		target="locale/$$language/LC_MESSAGES"; \
		mkdir -p $$target; \
		msgfmt --output=$$target/$(PACKAGE).mo $$po; \
	done

clean:
	rm -rf dist
	rm -rf build
	rm -rf locale

