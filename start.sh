#!/bin/bash

source ./venv/bin/activate

echo Starting core service..

python ./core.py &

sleep 1

echo Starting spotify_service..

python ./spotify_service.py &

sleep 1

echo Starting timer service...

python ./time_service.py &

sleep 1

echo Starting testing service...

python ./request_test.py