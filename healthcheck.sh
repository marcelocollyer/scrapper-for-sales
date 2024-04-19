#!/bin/bash

while true; do
  if ! curl -f http://localhost:8080/health; then
    echo "O serviço não está respondendo, reiniciando o container..."
    docker restart sales
  else
    echo "O serviço está operacional."
  fi
  sleep 30
done
