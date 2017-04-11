SCRIPTS=$(shell find . -name '*.py')
SOURCE=Spy

all: $(SCRIPTS) tmp/schema.svg

# install-tools:
# 	sudo apt-get install graphviz python3 findutils

clean:
	find doc/ -mindepth 1 -delete
	find . -name '*.pyc' -delete

tmp/schema.svg: schema/dot.py schema/data.py
	mkdir -p tmp
	python -m schema dot | dot -Tsvg > tmp/schema.svg


