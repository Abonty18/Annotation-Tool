#!/bin/bash

# Exit in case of error
set -e

# Ensure pip is available
python3 -m ensurepip

# Upgrade pip to the latest version
python3 -m pip install --upgrade pip

# Install Python dependencies directly without a virtual environment
python3 -m pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput

# List installed dependencies for debugging purposes
python3 -m pip freeze

# Print the current Python version for debugging
python3 --version
