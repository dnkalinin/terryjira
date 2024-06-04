#!/bin/bash
docker build - --tag=dnkalinin/terryjira:v1 < Dockerfile
docker run --name terryjira -v ${PWD}/bin:/tmp/bin -v ${PWD}/html:/html -p 8081:8081 -d -it dnkalinin/terryjira:v1

