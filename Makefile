# Author: Erik Anderson 
# Date Created: 02/27/2020

# Lints pyproject directory recursively
lint:
	pylint pyproject

# Type checks pyproject directory recursively
type:
	mypy pyproject

# Runs all tests in tests directory 
test:
	pytest
