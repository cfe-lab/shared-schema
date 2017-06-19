SCRIPTS=$(shell find . -name '*.py')
STATIC_FILES=$(shell find static -type f)

TEX_TABLES=$(shell find guides/ -name '*_table.tex')

all: docs/schema.svg docs/index.html static docs/schema.csv $(GUIDES) docs/schema.pdf docs/shared_clinical_guide.pdf

clean:
	find docs/ -mindepth 1 -delete
	find . -name '*.pyc' -delete
	find . -name '*.aux' -delete
	find . -name '*.log' -delete
	find tmp/ -mindepth 1 -delete

test:
	python3 -m unittest

docs/schema.svg: schema/dot.py schema/data.py
	python3 -m schema dot  | unflatten | dot -Tsvg > docs/schema.svg

docs/schema.csv: $(SCRIPTS)
	python3 -m schema csv > docs/schema.csv

static: $(STATIC_FILES)
	cp static/* docs/

docs/index.html: $(SCRIPTS)
	python3 -m schema index > docs/index.html


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

tmp/schema.tex: schema/tex.py schema/data.py tmp/schema.png  # limit to tex and data bc. slow
	python -m schema tex > tmp/schema.tex

tmp/schema.png: docs/schema.svg
	convert docs/schema.svg tmp/schema.png
