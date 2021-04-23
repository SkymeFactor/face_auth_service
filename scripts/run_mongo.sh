#!/bin/bash
docker run --rm --network=host --name=mongo -d mongo >/dev/null
docker exec -it mongo bash
docker stop mongo
