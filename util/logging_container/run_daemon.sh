#!/usr/bin/env bash

#docker kill $(docker ps -q -a)
#docker rm $(docker ps -q -a)

NAME=$1

echo 'start daemon A'
docker run --name BF-A${NAME} -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/bf2log.sh
sleep 20
docker run --name FTX-A${NAME} -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/ftx2log.sh
sleep 20
docker run --name BB-A${NAME} -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/bb2log.sh
sleep 20
docker run --name OK-A${NAME} -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/ok2log.sh


echo 'first daemon start----'
sleep 120

echo 'start daemon B'
docker run --name BF-B${NAME} -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/bf2log.sh
sleep 20
docker run --name FTX-B${NAME} -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/ftx2log.sh
sleep 20
docker run --name BB-B${NAME} -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/bb2log.sh
sleep 20
docker run --name OK-B${NAME} -d -v /bitlog:/bitlog --restart=always -t ftxmmf bash /ftxmmf/ok2log.sh





