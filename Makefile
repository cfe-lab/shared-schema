SCRIPTS=$(shell find . -name '*.py')
STATIC_FILES=$(shell find static -type f)

all: docs/schema.svg docs/index.html static docs/schema.csv $(GUIDES) docs/schema.pdf

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

docs/schema.csv: schema/csv.py schema/data.py
	python3 -m schema csv > docs/schema.csv

static: $(STATIC_FILES)
	cp static/* docs/

docs/index.html: $(SCRIPTS)
	python3 -m schema index > docs/index.html
# Schema document
docs/schema.pdf: tmp/schema.tex
	pdflatex -output-directory tmp tmp/schema.tex
	pdflatex -output-directory tmp tmp/schema.tex
	cp tmp/schema.pdf docs/schema.pdf

tmp/schema.tex: schema/tex.py schema/data.py tmp/schema.png
	python -m schema tex > tmp/schema.tex

tmp/schema.png: docs/schema.svg
	convert docs/schema.svg tmp/schema.png
