# Author: Erik Anderson
# Date Created: 02/27/2020

default: test

# Lints pyproject directory recursively
lint:
	pylint toolbox 

# Formats pyproject directory recursively
format:
	yapf -i -r toolbox 

# Type checks pyproject directory recursively
type:
	mypy toolbox 

# Runs all tests in tests directory
test:
	pytest

# Runs ctags 
tags:
	ctags -R .

.PHONY: lint format type test
