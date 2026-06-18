#!/bin/bash

source ./venv/bin/activate

echo Starting core service..

python ./core.py &

sleep 1

echo Starting spotify_service..

python ./spotify_service.py