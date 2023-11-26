#!/bin/bash

# Exit in case of error
set -e

# Ensure pip is available
python3 -m ensurepip

# Upgrade pip to the latest version
python3 -m pip install --upgrade pip

# Install Python dependencies directly without a virtual environment
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# List installed dependencies for debugging purposes
pip freeze

# No need to deactivate the virtual environment since we're not using one
