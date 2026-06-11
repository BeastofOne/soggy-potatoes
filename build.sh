#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Seed products on first deploy only — never overwrites live product edits
python manage.py seed_products

# Admin account recovery: no-op unless ADMIN_RESET_USERNAME/ADMIN_RESET_PASSWORD
# env vars are set in the Render dashboard (remove them after logging in)
python manage.py reset_admin_password
