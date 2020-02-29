# Author: Erik Anderson
# Date Created: 02/27/2020

default: test

# Lints pyproject directory recursively
lint:
	pylint pyproject

# Formats pyproject directory recursively
format:
	yapf -r pyproject

# Type checks pyproject directory recursively
type:
	mypy pyproject

# Runs all tests in tests directory
test:
	pytest

# Runs ctags 
tags:
	ctags -R .
