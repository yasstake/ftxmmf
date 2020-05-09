#!/bin/bash

export PYTHONPATH=/ftxmmf/

/usr/bin/python3.7 -m logger.bybit /bitlog
result=$?

# /usr/bin/python3.7 -m logger.upload /bitlog BF

if [ ${result} = 0 ]; then
    echo "sleep 50 min"
    sleep 3000
fi


