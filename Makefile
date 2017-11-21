PYTHON_SRC=$(shell find . -name '*.py')
TEMPLATES=$(shell find . -name '*.mustache')
TESTS=$(shell find test -name '*.py')
STATIC_FILES=$(shell find static -type f)
VBIN=./venv/bin

TEX_TABLES=$(shell find guides/ -name '*_table.tex')

all: docs/schema.svg docs/index.html docs/style.css docs/schema.csv $(GUIDES) docs/schema.pdf docs/shared_clinical_guide.pdf

venv:
	python3 -m venv venv
	${VBIN}/pip install -e '.[tests]'

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

docs/schema.svg: venv shared_schema/dot.py shared_schema/data.py
	${VBIN}/python -m shared_schema export dot  | unflatten | dot -Tsvg > docs/schema.svg

docs/schema.csv: venv $(PYTHON_SRC)
	${VBIN}/python -m shared_schema export csv > docs/schema.csv

docs/style.css: static/style.css
	cp static/style.css docs/

docs/index.html: venv $(PYTHON_SRC) $(TEMPLATES)
	${VBIN}/python -m shared_schema export html > docs/index.html


# Contributor/Analyst Guides
docs/shared_clinical_guide.pdf: guides/clinical.tex $(TEX_TABLES) tmp/clinical_relationships.png
	pdflatex -output-directory tmp guides/clinical.tex
	pdflatex -output-directory tmp guides/clinical.tex
	cp tmp/clinical.pdf docs/shared_clinical_guide.pdf

tmp/clinical_relationships.png: guides/clinical_relationships.dot
	dot -Tpng guides/clinical_relationships.dot > tmp/clinical_relationships.png


# Schema document
docs/schema.pdf: tmp/schema.tex
	pdflatex -output-directory tmp tmp/schema.tex
	pdflatex -output-directory tmp tmp/schema.tex
	cp tmp/schema.pdf docs/schema.pdf

tmp/schema.tex: venv shared_schema/tex.py shared_schema/data.py tmp/schema.png $(TEMPLATES)
	${VBIN}/python -m shared_schema export tex > tmp/schema.tex

tmp/schema.png: docs/schema.svg
	convert docs/schema.svg tmp/schema.png

FORCE:
