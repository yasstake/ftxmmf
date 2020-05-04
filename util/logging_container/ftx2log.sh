#!/bin/bash

export PYTHONPATH=/ftxmmf/

/usr/bin/python3.7 -m logger.ftx /bitlog
result=$?

# /usr/bin/python3.7 /mmf/upload.py /mexlog

if [ ${result} = 0 ]; then
    echo "sleep 50min"
    sleep 3000
fi


