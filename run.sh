#!/bin/bash
docker build - --tag=dnkalinin/terryjira:v1 < Dockerfile
docker run --name terryjira -v ${PWD}/bin:/tmp/pandas -v ${PWD}/html:/tmp/html -v ${PWD}/upload:/tmp/upload -p 8081:8081 -d -it dnkalinin/terryjira:v1

