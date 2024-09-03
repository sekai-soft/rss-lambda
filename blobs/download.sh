#!/bin/bash
set -e

# Download yolov3.weights if not already exists
if [ ! -f yolov3.weights ]; then
    echo "Downloading yolov3.weights"
    wget https://pjreddie.com/media/files/yolov3.weights -O yolov3.weights
fi

# Download yolov3.cfg if not already exists
if [ ! -f yolov3.cfg ]; then
    echo "Downloading yolov3.cfg"
    wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg -O yolov3.cfg
fi
