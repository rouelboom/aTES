PROJECT_NAME ?= task-tracker
# if 'v' variable exists, VERSION=v, else get from setup.py
# Example: make version v=1.0.0
VERSION = $(or $(v), $(shell python3 setup.py --version | tr '+' '-'))
PYTHON_PATH = $(or $(path), $(shell which python3))

NEXUS_DOMAIN = 'nexus.opo'
PIP_NEXUS_URL = 'http://$(NEXUS_DOMAIN)/repository/pip-internal/simple/'


all:
	@echo "make clean				- Remove files created by distutils"
	@echo "make cleanvenv				- Remove files created by venv"
	@echo "make devenv [path=<python_path>]	- Create & setup development virtual environment"
	@echo "make getfreeze				- Write pip packages to requirements.freeze.txt"
	@echo "make build				- Make source distribution"
	@echo "make deb [v=<version>]			- Create deb package from source"
	@echo "make package [v=<version>]		- Create deb package"
	@echo "make version				- Show version info"
	@exit 0

clean:
	rm -rf *.egg-info dist ./deb/*.deb pip-cache

cleanvenv:
	rm -rf venv

devenv: clean cleanvenv
	# создаем новое окружение и устанавливаем основные + dev зависимости
	# из extras_require (см. setup.py)
	$(PYTHON_PATH) -m venv venv
	venv/bin/pip install --upgrade pip setuptools
	venv/bin/pip install --extra-index-url $(PIP_NEXUS_URL) --trusted-host $(NEXUS_DOMAIN) -Ue '.[test]'

getfreeze: devenv
	venv/bin/pip freeze > requirements.freeze.txt
	make cleanvenv

build: clean
	python3 setup.py sdist

deb: build
	bash deb/build.sh $(VERSION)

download-deps:
	mkdir pip-cache
	pip3 download pip wheel -d pip-cache
	pip3 download -r requirements.txt -d pip-cache --extra-index-url=http://nexus.opo/repository/pip-internal/simple/ --trusted-host nexus.opo

package: clean build download-deps deb

version:
	@echo "Module: $(PROJECT_NAME)"
	@echo "Version: $(VERSION)"

.PHONY: all clean cleanvenv devenv getfreeze build deb package version download-deps
