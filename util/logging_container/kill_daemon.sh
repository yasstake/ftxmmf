#!/usr/bin/env bash

docker kill $(docker ps -q -a)
docker rm $(docker ps -q -a)
