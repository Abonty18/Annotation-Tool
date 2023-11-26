#!/bin/bash
echo "BUILD START"
# Exit in case of error
set -e

# Install system dependencies, for example, Python 3.9 and PostgreSQL
# This is just an example, as Vercel's build environment already includes Python

# Install Python dependencies
pip install -r requirements.txt

# Collect static files into the 'staticfiles' directory
python manage.py collectstatic --no-input --clear

# Apply migrations (Not recommended for production, handle migrations separately)
# python manage.py migrate

# Create a directory for static files build
mkdir -p staticfiles_build

# Move collected static files to the static files build directory
mv staticfiles/* staticfiles_build/

# Clean up
rm -rf staticfiles

# Note: Additional steps might be required depending on your project's needs
