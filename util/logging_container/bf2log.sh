#!/bin/bash

export PYTHONPATH=/ftxmmf/

/usr/bin/python3.7 -m logger.bf /bitlog
result=$?

# /usr/bin/python3.7 -m logger.upload /bitlog BF

if [ ${result} = 0 ]; then
    echo "sleep 30 sec"
    sleep 30
    #sleep 3000
fi


