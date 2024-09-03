#!/bin/bash
set -e

if [ -n "$DOWNLOAD_YOLOV3_BLOBS" ]; then
    pushd blobs
    ./download.sh
    popd
fi

PORT="${PORT:=5000}"
gunicorn --bind 0.0.0.0:${PORT} --workers 1 app:app
