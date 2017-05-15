SCRIPTS=$(shell find . -name '*.py')
STATIC_FILES=$(shell find static -type f)

all: docs/schema.svg docs/index.html static docs/schema.csv

clean:
	find docs/ -mindepth 1 -delete
	find . -name '*.pyc' -delete

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
