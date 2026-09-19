#!/bin/bash

source ./venv/bin/activate

echo Starting core.service...

python ./core.py &

sleep 1

echo Starting spotify.service...

python ./spotify_service.py &

sleep 1

echo Starting timer.service...

python ./time_service.py &

sleep 1

echo Starting audio_input.service...

python ./audio_input.py &

sleep 1

echo Starting STT.service...

python ./stt_service.py &

sleep 1

echo starting voice_detection.service...

python ./voice-detection.py &

sleep 1

echo Starting testing service...

python ./request_test.py