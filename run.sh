#!/bin/bash

docker build -t mm .
docker rm mm --force
docker run -d -p 8008:8008 --name mm mm
