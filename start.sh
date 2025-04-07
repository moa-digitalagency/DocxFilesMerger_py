#!/bin/bash
# Run the documentation server
cd "$(dirname "$0")"
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload cli_app:app
