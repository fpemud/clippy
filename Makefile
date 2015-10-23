PACKAGE_VERSION=0.0.1
prefix=/usr

clean:

install:
	install -d -m 0755 "$(DESTDIR)/$(prefix)/bin"
	install -m 0755 clippy "$(DESTDIR)/$(prefix)/bin"

	install -d -m 0755 "$(DESTDIR)/$(prefix)/lib/clippy"
	cp -r lib/* "$(DESTDIR)/$(prefix)/lib/clippy"
	find "$(DESTDIR)/$(prefix)/lib/clippy" -type f | xargs chmod 644
	find "$(DESTDIR)/$(prefix)/lib/clippy" -type d | xargs chmod 755

	install -d -m 0755 "$(DESTDIR)/$(prefix)/share/clippy"
	cp -r agents/* "$(DESTDIR)/$(prefix)/share/clippy"
	find "$(DESTDIR)/$(prefix)/share/clippy" -type f | xargs chmod 644
	find "$(DESTDIR)/$(prefix)/share/clippy" -type d | xargs chmod 755

uninstall:
	rm -Rf "$(DESTDIR)/$(prefix)/bin/clippy"
	rm -Rf "$(DESTDIR)/$(prefix)/lib/clippy"

.PHONY: clean install uninstall
