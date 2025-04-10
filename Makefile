DESTDIR=
PREFIX=
NAME=python-azuremetadata
dirs=lib man
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
	PYTHONPATH=./lib pytest --cov-report html --cov=lib/ --cov-report term-missing

clean:
	rm -rf lib/azuremetadata/__pycache__

tar: clean
	mkdir "$(NAME)-$(verSrc)"
	cp -r $(dirs) $(files) "$(NAME)-$(verSrc)"
	tar -cjf "$(NAME)-$(verSrc).tar.bz2" "$(NAME)-$(verSrc)"
	rm -rf "$(NAME)-$(verSrc)"

install:
	python3 setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"

