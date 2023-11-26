

# Exit in case of error
set -e

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply migrations (optional and not recommended for production)
# python manage.py migrate

# Deactivate the virtual environment
deactivate
