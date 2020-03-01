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
    export MYPYPATH=$PWD/toolbox
else
    export MYPYPATH=$PWD/toolbox:$MYPYPATH
fi

# Set TOOLBOX_HOME variable
export TOOLBOX_HOME=$PWD
