# Soggy Potatoes Sticker Shop

E-commerce website for Joana's sticker shop with community features.

## Quick Start

```bash
# Navigate to project
cd /Users/jacobphillips/Desktop/soggy-potatoes

# Activate virtual environment
source venv/bin/activate

# Run the development server
python manage.py runserver

# Access at: http://localhost:8000
# Admin at: http://localhost:8000/admin
```

## First Time Setup

If setting up for the first time after cloning:

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env  # Then edit .env with your settings

# Start PostgreSQL
brew services start postgresql@16

# Create database
createdb soggy_potatoes

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Project Structure

```
soggy-potatoes/
├── docs/                   # Documentation
├── shop/                   # E-commerce app
├── forum/                  # Community forum app
├── users/                  # User authentication app
├── soggy_potatoes/         # Django project settings
├── static/                 # Global static files
├── templates/              # Global templates
├── media/                  # User uploads
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (DO NOT COMMIT)
└── manage.py               # Django CLI
```

## Documentation

- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [System Operations Manual](docs/SYSTEM_OPERATIONS_MANUAL.md)
- [Technical Protocols](docs/TECHNICAL_PROTOCOLS.md)
- [Development Log](docs/DEVELOPMENT_LOG.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING_GUIDE.md)

## Technology Stack

- **Framework:** Django 5.2
- **Database:** PostgreSQL 16
- **Frontend:** Django Templates + Bootstrap 5
- **Payments:** Stripe (Phase 6)
- **Email:** SendGrid

## Current Phase

**Phase 0: Setup & Planning** - Complete
**Phase 1: Core Infrastructure** - Starting

---

*For Joana, with love.*
