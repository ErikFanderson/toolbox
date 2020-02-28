#!/usr/bin/env bash 

# Set PYTHONPATH accordingly
if [ -z "$PYTHONPATH" ]
then
    export PYTHONPATH=$PWD
else
    export PYTHONPATH=$PWD:$PYTHONPATH
fi

# Set MYPYPATH accordingly
if [ -z "$MYPYPATH" ]
then
    export MYPYPATH=$PWD/pyproject
else
    export MYPYPATH=$PWD/pyproject:$MYPYPATH
fi

# Set PYPROJECT_HOME variable
export PYPROJECT_HOME=$PWD

