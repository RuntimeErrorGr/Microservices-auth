#!/bin/sh
export FLASK_DEBUG=0
gunicorn -w 1 --threads 4 --timeout 120 --bind 0.0.0.0:5000 manage:app
exec "$@"