#!/bin/bash
docker build ../ -t id_service
docker run --rm -it -p 5000:5000 id_service
docker rmi id_service