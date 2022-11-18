#!/usr/bin/env bash

# Set PYTHONPATH accordingly
if [ -z "$PYTHONPATH" ]
then
    export PYTHONPATH=$PWD/src
else
    export PYTHONPATH=$PWD/src:$PYTHONPATH
fi
