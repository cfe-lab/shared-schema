SCRIPTS=$(shell find . -name '*.py')
TEMPLATES=$(shell find . -name '*.mustache')
TESTS=$(shell find test -name '*.py')
STATIC_FILES=$(shell find static -type f)

TEX_TABLES=$(shell find guides/ -name '*_table.tex')

all: docs/schema.svg docs/index.html docs/style.css docs/schema.csv $(GUIDES) docs/schema.pdf docs/shared_clinical_guide.pdf

clean:
	find docs/ -mindepth 1 -delete
	git checkout docs/
	find . -name '*.pyc' -delete
	find . -name '*.aux' -delete
	find . -name '*.log' -delete
	find tmp/ -mindepth 1 -delete

test: $(SCRIPTS) $(TESTS) FORCE
	python3 -m unittest -b
	pep8 shared_schema

docs/schema.svg: shared_schema/dot.py shared_schema/data.py
	python3 -m shared_schema dot  | unflatten | dot -Tsvg > docs/schema.svg

docs/schema.csv: $(SCRIPTS)
	python3 -m shared_schema csv > docs/schema.csv

docs/style.css: static/style.css
	cp static/style.css docs/

docs/index.html: $(SCRIPTS) $(TEMPLATES)
	python3 -m shared_schema html > docs/index.html


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

tmp/schema.tex: shared_schema/tex.py shared_schema/data.py tmp/schema.png $(TEMPLATES)
	python -m shared_schema tex > tmp/schema.tex

tmp/schema.png: docs/schema.svg
	convert docs/schema.svg tmp/schema.png

FORCE:
