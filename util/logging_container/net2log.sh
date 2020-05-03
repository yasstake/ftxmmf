#!/bin/bash

worker_name=$1

export PYTHONPATH=/ftxmmf/

LOGDIR=/logdir/

/usr/bin/python3.7 -m logger.bf
result=$?

# /usr/bin/python3.7 /mmf/upload.py /mexlog

if [ $result = 0 ]; then
    echo "sleep 50min"
    sleep 3000
fi


