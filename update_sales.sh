#!/bin/bash

docker stop sales
docker system prune -af
docker run -d --rm --env-file sales.env -p 8080:8080 --name sales marcelocollyer/sales-scrapper-py:latest
docker ps