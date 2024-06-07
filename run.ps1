Get-Content Dockerfile | docker build - --tag=dnkalinin/terryjira:v1

docker run --name terryjira -v ${PWD}/bin:/usr/local/sbin -v ${PWD}/html:/html -p 8081:8081 -d -it dnkalinin/terryjira:v1
