#!/bin/bash

while true; do
  if ! curl -f http://localhost:8080/health; then
    echo "Service not responding. Container will get recycled..."
    docker restart sales
  else
    echo "Service is up!"
  fi
  sleep 30
done
