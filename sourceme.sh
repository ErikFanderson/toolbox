#!/usr/bin/env bash 

# Set PYTHONPATH accordingly
if [ -z "$PYTHONPATH" ]
then
    export PYTHONPATH=$PWD:$PWD/toolbox/Yamale
else
    export PYTHONPATH=$PWD:$PWD/toolbox/Yamale:$PYTHONPATH
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

# Add to path
export PATH=$TOOLBOX_HOME/bin:$PATH
