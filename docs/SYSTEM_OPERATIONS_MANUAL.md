# System Operations Manual

**Project:** Soggy Potatoes Sticker Shop
**Last Updated:** January 16, 2026
**Purpose:** How to run, maintain, and operate the system

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Development Environment](#development-environment)
3. [Running the Application](#running-the-application)
4. [Database Operations](#database-operations)
5. [Common Tasks](#common-tasks)
6. [Backup & Recovery](#backup--recovery)
7. [Deployment](#deployment)

---

## Quick Start

### First Time Setup

```bash
# 1. Navigate to project
cd /Users/jacobphillips/Desktop/soggy-potatoes

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up database
python manage.py migrate

# 5. Create admin user (first time only)
python manage.py createsuperuser

# 6. Run the server
python manage.py runserver
```

### Daily Development

```bash
# Navigate and activate
cd /Users/jacobphillips/Desktop/soggy-potatoes
source venv/bin/activate

# Run server
python manage.py runserver

# Access at: http://localhost:8000
# Admin at: http://localhost:8000/admin
```

---

## Development Environment

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| Python | 3.11+ | Runtime | `brew install python@3.11` |
| PostgreSQL | 16 | Database | `brew install postgresql@16` |
| Git | Latest | Version control | `brew install git` |
| pip | Latest | Package manager | Comes with Python |

### Virtual Environment

**Why:** Isolates project dependencies from system Python.

```bash
# Create (one time)
python3 -m venv venv

# Activate (every session)
source venv/bin/activate

# Deactivate (when done)
deactivate

# Verify activated (should show project path)
which python
```

### Environment Variables

Location: `/Users/jacobphillips/Desktop/soggy-potatoes/.env`

**NEVER commit this file to Git!**

```bash
# .env template
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://user:password@localhost:5432/soggy_potatoes
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your-sendgrid-username
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
```

---

## Running the Application

### Development Server

```bash
# Standard run
python manage.py runserver

# Run on different port
python manage.py runserver 8080

# Run accessible from network (for testing on phone)
python manage.py runserver 0.0.0.0:8000
```

### Access Points

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | Main site |
| http://localhost:8000/admin | Admin panel |
| http://localhost:8000/shop | Product listings |
| http://localhost:8000/forum | Community forum |
| http://localhost:8000/account | User account |

### Stopping the Server

Press `Ctrl + C` in the terminal.

---

## Database Operations

### PostgreSQL Service

```bash
# Start PostgreSQL
brew services start postgresql@16

# Stop PostgreSQL
brew services stop postgresql@16

# Check status
brew services list
```

### Django Database Commands

```bash
# Apply migrations (after model changes)
python manage.py migrate

# Create new migration (after changing models.py)
python manage.py makemigrations

# Show migration status
python manage.py showmigrations

# Reset database (DESTRUCTIVE - deletes all data)
python manage.py flush
```

### Database Access

```bash
# Django database shell
python manage.py dbshell

# Or direct PostgreSQL access
psql -d soggy_potatoes
```

### Useful Database Queries

```sql
-- List all tables
\dt

-- Count products
SELECT COUNT(*) FROM shop_product;

-- Count users
SELECT COUNT(*) FROM auth_user;

-- Count orders
SELECT COUNT(*) FROM shop_order;
```

---

## Common Tasks

### Adding a New Product (via Admin)

1. Go to http://localhost:8000/admin
2. Log in with superuser credentials
3. Click "Products" under SHOP
4. Click "Add Product" button
5. Fill in: Name, Description, Price, Image, Category
6. Click "Save"

### Adding a New Product (via Shell)

```bash
python manage.py shell
```

```python
from shop.models import Product, Category

# Get or create category
category, created = Category.objects.get_or_create(name="Stickers")

# Create product
product = Product.objects.create(
    name="Cute Potato Sticker",
    description="An adorable soggy potato sticker",
    price=3.99,
    category=category,
    stock=100
)
print(f"Created: {product}")
```

### Creating a Superuser

```bash
python manage.py createsuperuser
# Follow prompts for username, email, password
```

### Resetting a User Password

```bash
python manage.py changepassword username
```

### Collecting Static Files (for Production)

```bash
python manage.py collectstatic
```

### Running Tests

```bash
# All tests
python manage.py test

# Specific app tests
python manage.py test shop
python manage.py test forum
python manage.py test users

# With verbosity
python manage.py test -v 2
```

---

## Backup & Recovery

### Database Backup

```bash
# Create backup
pg_dump soggy_potatoes > backup_$(date +%Y%m%d_%H%M%S).sql

# Recommended: Store in separate location
cp backup_*.sql ~/Dropbox/soggy-potatoes-backups/
```

### Database Restore

```bash
# Restore from backup (OVERWRITES current data)
psql soggy_potatoes < backup_20260116_120000.sql
```

### Media Files Backup

```bash
# Backup uploaded images/files
tar -czvf media_backup_$(date +%Y%m%d).tar.gz media/
```

### Full Project Backup

```bash
# Backup entire project (excluding venv and __pycache__)
tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
    -czvf soggy_potatoes_backup_$(date +%Y%m%d).tar.gz \
    /Users/jacobphillips/Desktop/soggy-potatoes/
```

### Backup Schedule Recommendation

| What | Frequency | Retention |
|------|-----------|-----------|
| Database | Daily | 7 days |
| Media files | Weekly | 4 weeks |
| Full project | Before major changes | 3 versions |

---

## Deployment

### Pre-Deployment Checklist

- [ ] All tests passing (`python manage.py test`)
- [ ] No debug prints in code
- [ ] Environment variables configured
- [ ] Static files collected
- [ ] Database migrations committed
- [ ] .env not in Git
- [ ] DEBUG=False for production

### Deploy to Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Set environment variables
railway variables set SECRET_KEY=xxx
railway variables set DEBUG=False
railway variables set DATABASE_URL=xxx
```

### Deploy to Render

1. Connect GitHub repository to Render
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn soggy_potatoes.wsgi:application`
5. Add environment variables in dashboard
6. Deploy

### Post-Deployment

```bash
# Run migrations on production
railway run python manage.py migrate

# Create superuser on production
railway run python manage.py createsuperuser
```

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| "No module named..." | Activate venv: `source venv/bin/activate` |
| Database connection error | Start PostgreSQL: `brew services start postgresql@16` |
| Migration errors | See TROUBLESHOOTING_GUIDE.md |
| Static files not loading | Run `python manage.py collectstatic` |
| Permission denied | Check file permissions, may need `chmod` |

**For detailed troubleshooting, see:** [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)

---

## Document Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-16 | 1.0 | Initial manual created | Claude |

---

*End of System Operations Manual*
