SCRIPTS=$(shell find . -name '*.py')
STATIC_FILES=$(shell find static -type f)

all: doc/schema.svg doc/index.html static

clean:
	find doc/ -mindepth 1 -delete
	find . -name '*.pyc' -delete

test:
	python3 -m unittest

doc/schema.svg: schema/dot.py schema/data.py
	python -m schema dot | dot -Tsvg > doc/schema.svg

static: $(STATIC_FILES)
	cp static/* doc/

doc/index.html: $(SCRIPTS)
	python -m schema index > doc/index.html
