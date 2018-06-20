PYTHON_SRC=$(shell find . -name '*.py')
TEMPLATES=$(shell find . -name '*.mustache')
TESTS=$(shell find test -name '*.py')
STATIC_FILES=$(shell find static -type f)
VBIN=./venv/bin

venv:
	python3 -m venv venv
	${VBIN}/pip install -e '.[tests]'
	${VBIN}/pip install -r dev-tools.txt

clean:
	find docs/ -mindepth 1 -delete
	git checkout docs/
	find . -name '*.pyc' -delete
	find . -name '*.aux' -delete
	find . -name '*.log' -delete
	find tmp/ -mindepth 1 -delete
	rm -r venv

test: $(PYTHON_SRC) $(TESTS) FORCE venv
	${VBIN}/python -m unittest

check: venv $(PYTHON_SRC) $(TESTS) FORCE test
	${VBIN}/pycodestyle shared_schema
	${VBIN}/pycodestyle test
	${VBIN}/flake8 shared_schema
	${VBIN}/flake8 test


# Schema document
FORCE:
