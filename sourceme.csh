#!/usr/bin/env csh 

# Set PYTHONPATH accordingly
if (! $?PYTHONPATH) then
    setenv PYTHONPATH $PWD\:$PWD/toolbox/Yamale
else
    setenv PYTHONPATH $PWD\:$PWD/toolbox/Yamale\:$PYTHONPATH
endif

# Set MYPYPATH accordingly
if (! $?MYPYPATH) then
    setenv MYPYPATH $PWD/toolbox
else
    setenv MYPYPATH $PWD/toolbox\:$MYPYPATH
endif

# Set TOOLBOX_HOME variable
setenv TOOLBOX_HOME $PWD

## Add to path
setenv PATH $TOOLBOX_HOME/bin\:$PATH
