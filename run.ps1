Get-Content Dockerfile | docker build - --tag=dnkalinin/terryjira:v1

docker run --name terryjira -v ${PWD}/bin:/tmp/bin -v ${PWD}/html:/html -v ${PWD}/upload:/upload -p 8081:8081 -d -it dnkalinin/terryjira:v1
