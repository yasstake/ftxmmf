#!/usr/bin/env bash

docker kill $(docker ps -q -a)
docker rm $(docker ps -q -a)

echo 'start daemon A'
docker run --name BF-A -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/bf2log.sh
sleep 1
docker run --name FTX-A -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/ftx2log.sh

sleep 30

echo 'start daemon B'
docker run --name BF-B -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/bf2log.sh
sleep 1
docker run --name FTX-B -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/ftx2log.sh





