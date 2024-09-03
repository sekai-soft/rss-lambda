#!/bin/bash
set -e

PORT="${PORT:=5000}"
gunicorn --bind 0.0.0.0:${PORT} --workers 1 app:app --timeout 300
