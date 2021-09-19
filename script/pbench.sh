#!/bin/bash

curl http://localhost:6379

while [ "$?" != 52 ]
do
    sleep 0.5
    curl http://localhost:6379
done

/runner.sh
