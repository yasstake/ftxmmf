#!/bin/bash

export PYTHONPATH=/ftxmmf/

/usr/bin/python3.7 -m logger.ftx /bitlog
result=$?

# /usr/bin/python3.7 -m logger.upload /bitlog FTX

if [ ${result} = 0 ]; then
    echo "sleep 50min"
    sleep 3000
fi


