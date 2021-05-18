#!/bin/bash
docker run --rm -v $(pwd)/.database:/data/db --network=host --name=mongo -d mongo >/dev/null
docker exec -it mongo bash
docker stop mongo
