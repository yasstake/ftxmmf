#!/bin/bash

worker_name=$1

export PYTHONPATH=/ftxmmf/


/usr/bin/python3.7 -m logger.bf /bitlog
result=$?

# /usr/bin/python3.7 -m logger.upload /bitlog BF

if [ ${result} = 0 ]; then
    echo "sleep 50min"
    sleep 3000
fi


