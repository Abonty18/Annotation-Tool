#!/bin/bash

# Exit in case of error
set -e

# Get the current directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create a virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
  python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate the virtual environment using an absolute path
source "$SCRIPT_DIR/venv/bin/activate"

# Upgrade pip to the latest version
pip install --upgrade pip

# Install Python dependencies in the virtual environment
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# After installing dependencies, list them
pip freeze

# Print the current Python path
echo $PYTHONPATH

# Print the location of the Django package
python -c "import django; print(django.__path__)"

# Deactivate the virtual environment
deactivate
