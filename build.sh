#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Load product data (only adds new items, won't duplicate)
python manage.py loaddata fixtures/products.json || echo "Fixture loading skipped or already loaded"
