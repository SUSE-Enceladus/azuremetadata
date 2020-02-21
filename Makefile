DESTDIR=
PREFIX=
NAME=python3-azuremetadata
dirs=lib
files=Makefile README.md LICENSE azuremetadata setup.py

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}\n' *.spec)
verSpec = $(shell rpm -q --specfile --qf '%{VERSION}' *.spec)
verSrc = $(shell cat lib/azuremetadata/VERSION)
ifneq "$(verSpec)" "$(verSrc)"
$(error "Version mismatch, will not take any action")
endif

test:
	PYTHONPATH=./lib pytest

coverage:
	PYTHONPATH=./lib pytest --cov-report html --cov=lib/

tar:
	mkdir "$(NAME)-$(verSrc)"
	cp -r $(dirs) $(files) "$(NAME)-$(verSrc)"
	tar -cjf "$(NAME)-$(verSrc).tar.bz2" "$(NAME)-$(verSrc)"
	rm -rf "$(NAME)-$(verSrc)"

install:
	python setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"

