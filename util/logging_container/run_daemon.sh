#!/usr/bin/env bash

docker kill $(docker ps -q -a)
docker rm $(docker ps -q -a)

echo 'start daemon A'
docker run --name WORKER-A -d -v /tmp:/bitlog --restart=always -t ftxmmf bash /net2log.sh

sleep 10

echo 'start daemon B'
docker run --name WORKER-B -d -v /tmp:/bitlog --restart=always -t ftxmmf bash /net2log.sh





