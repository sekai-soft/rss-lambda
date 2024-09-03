#!/bin/bash
set -e

if [ -n "$DOWNLOAD_YOLOV3_BLOBS" ]; then
    # Download yolov3.weights if not already exists
    if [ ! -f blobs/yolov3.weights ]; then
        echo "Downloading yolov3.weights"
        wget https://pjreddie.com/media/files/yolov3.weights -O blobs/yolov3.weights
    fi

    # Download yolov3.cfg if not already exists
    if [ ! -f blobs/yolov3.cfg ]; then
        echo "Downloading yolov3.cfg"
        wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg -O blobs/yolov3.cfg
    fi
fi

PORT="${PORT:=5000}"
gunicorn --bind 0.0.0.0:${PORT} --workers 1 app:app
