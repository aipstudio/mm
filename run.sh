#!/bin/bash

WD=/root/mm
cd $WD
#git clone https://github.com/aipstudio/mm.git $WD
#git pull

docker build -t mm .
docker rm mm --force
docker run -d -p 8008:8008 --name mm mm

