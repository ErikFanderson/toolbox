# Author: Erik Anderson
# Date Created: 02/27/2020

TESTS=tests
SRC=toolbox
DIRS = $(SRC) $(TESTS)

default: test

# Lints pyproject directory recursively
lint:
	pylint $(DIRS) 

# Formats pyproject directory recursively
format:
	yapf -i -r $(DIRS) -e toolbox/Yamale 

# Type checks pyproject directory recursively
type:
	mypy $(DIRS) 

# Runs all tests in tests directory
test:
	pytest $(TESTS) -v
	rm -rf build/ toolbox.yml

# Runs ctags 
tags:
	ctags -R .

clean:
	rm -rf build/ tags

.PHONY: lint format type test clean
