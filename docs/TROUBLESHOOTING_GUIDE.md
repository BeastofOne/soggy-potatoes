# Troubleshooting Guide

**Project:** Soggy Potatoes Sticker Shop
**Last Updated:** January 16, 2026
**Purpose:** Solutions to common issues and errors

---

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [Environment Issues](#environment-issues)
3. [Database Issues](#database-issues)
4. [Django Issues](#django-issues)
5. [Template & Static Files](#template--static-files)
6. [Authentication Issues](#authentication-issues)
7. [Payment Issues](#payment-issues)
8. [Deployment Issues](#deployment-issues)
9. [Performance Issues](#performance-issues)

---

## Quick Diagnosis

### Error Message Lookup

| Error | Likely Cause | Jump To |
|-------|--------------|---------|
| `ModuleNotFoundError` | Virtual env not activated | [ENV-001](#env-001) |
| `No such file or directory: 'python'` | Python not installed | [ENV-002](#env-002) |
| `connection refused` | Database not running | [DB-001](#db-001) |
| `relation does not exist` | Migrations not run | [DB-002](#db-002) |
| `CSRF verification failed` | Missing CSRF token | [DJ-003](#dj-003) |
| `TemplateDoesNotExist` | Wrong template path | [TS-001](#ts-001) |
| `Static file not found` | collectstatic needed | [TS-002](#ts-002) |

### Health Check Commands

```bash
# Check Python
python --version

# Check virtual env is active
which python  # Should show project venv path

# Check PostgreSQL is running
brew services list | grep postgresql

# Check Django can start
python manage.py check

# Check database connection
python manage.py dbshell

# Check migrations status
python manage.py showmigrations
```

---

## Environment Issues

### ENV-001: ModuleNotFoundError {#env-001}

**Symptom:**
```
ModuleNotFoundError: No module named 'django'
```

**Cause:** Virtual environment not activated or package not installed.

**Solution:**
```bash
# 1. Activate virtual environment
cd /Users/jacobphillips/Desktop/soggy-potatoes
source venv/bin/activate

# 2. Verify activation (should show venv path)
which python

# 3. If still failing, reinstall packages
pip install -r requirements.txt
```

---

### ENV-002: Python Not Found {#env-002}

**Symptom:**
```
zsh: command not found: python
```

**Cause:** Python not installed or not in PATH.

**Solution:**
```bash
# Check if python3 works
python3 --version

# If yes, use python3 instead, or create alias
echo 'alias python=python3' >> ~/.zshrc
source ~/.zshrc

# If not, install Python
brew install python@3.11
```

---

### ENV-003: Virtual Environment Creation Fails

**Symptom:**
```
Error: Command 'venv' not found
```

**Solution:**
```bash
# Use python3 explicitly
python3 -m venv venv

# If that fails, install venv
pip3 install virtualenv
virtualenv venv
```

---

### ENV-004: Permission Denied

**Symptom:**
```
Permission denied: '/Users/.../venv/bin/activate'
```

**Solution:**
```bash
# Fix permissions
chmod +x venv/bin/activate

# Or recreate venv
rm -rf venv
python3 -m venv venv
```

---

## Database Issues

### DB-001: Connection Refused {#db-001}

**Symptom:**
```
psycopg2.OperationalError: connection refused
Is the server running on host "localhost"?
```

**Cause:** PostgreSQL service not running.

**Solution:**
```bash
# Start PostgreSQL
brew services start postgresql@16

# Verify it's running
brew services list

# If it won't start, check logs
tail -100 /opt/homebrew/var/log/postgresql@16.log
```

---

### DB-002: Relation Does Not Exist {#db-002}

**Symptom:**
```
django.db.utils.ProgrammingError: relation "shop_product" does not exist
```

**Cause:** Database migrations haven't been run.

**Solution:**
```bash
# Run all migrations
python manage.py migrate

# If that fails, check migration status
python manage.py showmigrations

# If migrations are missing, create them
python manage.py makemigrations
python manage.py migrate
```

---

### DB-003: Database Does Not Exist

**Symptom:**
```
FATAL: database "soggy_potatoes" does not exist
```

**Solution:**
```bash
# Create the database
createdb soggy_potatoes

# Or via psql
psql postgres
CREATE DATABASE soggy_potatoes;
\q
```

---

### DB-004: Migration Conflicts

**Symptom:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:**
```bash
# Option 1: Fake the migration
python manage.py migrate --fake app_name migration_name

# Option 2: Reset migrations (DEVELOPMENT ONLY - loses data)
python manage.py migrate app_name zero
rm app_name/migrations/0*.py
python manage.py makemigrations app_name
python manage.py migrate app_name
```

---

### DB-005: Cannot Connect After Password Change

**Symptom:** Authentication failed after changing PostgreSQL password.

**Solution:**
```bash
# Update .env file with new password
DATABASE_URL=postgres://user:NEW_PASSWORD@localhost:5432/soggy_potatoes

# Restart Django server
```

---

## Django Issues

### DJ-001: Secret Key Error

**Symptom:**
```
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty
```

**Solution:**
```bash
# 1. Check .env file exists
ls -la .env

# 2. Check SECRET_KEY is set
grep SECRET_KEY .env

# 3. If missing, generate one
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Add to .env
echo 'SECRET_KEY=your-generated-key-here' >> .env
```

---

### DJ-002: Import Error in Settings

**Symptom:**
```
ImportError: cannot import name 'config' from 'decouple'
```

**Solution:**
```bash
# Install python-decouple
pip install python-decouple

# Or if using dotenv
pip install python-dotenv
```

---

### DJ-003: CSRF Verification Failed {#dj-003}

**Symptom:**
```
Forbidden (403) - CSRF verification failed
```

**Cause:** Missing `{% csrf_token %}` in form.

**Solution:**
```html
<!-- Add to your form -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

For AJAX requests:
```javascript
// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Include in AJAX request
fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
```

---

### DJ-004: URL Not Found (404)

**Symptom:**
```
Page not found (404)
```

**Diagnosis:**
```bash
# List all URLs
python manage.py show_urls  # Requires django-extensions

# Or check urls.py manually
```

**Common Causes:**
1. URL pattern not defined
2. Missing trailing slash
3. App URLs not included in main urls.py
4. Typo in URL name

---

### DJ-005: Server Won't Start

**Symptom:**
```
Error: That port is already in use.
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 PID_NUMBER

# Or use different port
python manage.py runserver 8080
```

---

## Template & Static Files

### TS-001: TemplateDoesNotExist {#ts-001}

**Symptom:**
```
django.template.exceptions.TemplateDoesNotExist: shop/product_list.html
```

**Checklist:**
1. File exists at correct path?
2. TEMPLATES setting includes app directories?
3. App is in INSTALLED_APPS?

**Solution:**
```python
# settings.py - ensure this is set
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Project-level templates
        'APP_DIRS': True,  # Allows app/templates/ lookup
        ...
    },
]

# Ensure app is installed
INSTALLED_APPS = [
    ...
    'shop',  # Must be listed
]
```

**Template location should be:**
```
shop/
└── templates/
    └── shop/
        └── product_list.html  # shop/product_list.html
```

---

### TS-002: Static Files Not Loading {#ts-002}

**Symptom:** CSS/JS/images not loading, 404 errors for static files.

**Development Solution:**
```python
# settings.py
DEBUG = True  # Static files served automatically in debug mode

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Project-level static
```

**Production Solution:**
```bash
# Collect all static files
python manage.py collectstatic

# Ensure STATIC_ROOT is set
# settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

### TS-003: Images Not Displaying

**Symptom:** Uploaded images show broken image icon.

**Solution:**
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# urls.py (development only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Authentication Issues

### AUTH-001: Login Not Working

**Symptom:** Login form submits but user not authenticated.

**Checklist:**
1. User exists in database?
2. Password correct?
3. User is_active = True?
4. LOGIN_REDIRECT_URL set?

**Debug:**
```python
# In Django shell
python manage.py shell

from django.contrib.auth.models import User
user = User.objects.get(username='testuser')
print(user.is_active)  # Should be True
print(user.check_password('password'))  # Should be True
```

---

### AUTH-002: Logout Not Working

**Symptom:** After logout, still appears logged in.

**Solution:**
```python
# views.py
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')  # Must redirect after logout

# urls.py
path('logout/', logout_view, name='logout'),
```

---

### AUTH-003: Password Reset Email Not Sending

**Symptom:** Password reset requested but no email received.

**Checklist:**
1. Email settings configured?
2. SendGrid API key valid?
3. Check spam folder

**Debug:**
```python
# settings.py - for testing, use console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# This prints emails to console instead of sending
```

---

## Payment Issues

### PAY-001: Stripe Key Errors

**Symptom:**
```
stripe.error.AuthenticationError: Invalid API Key
```

**Solution:**
```bash
# Check .env has correct keys
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Verify in Django shell
python manage.py shell
import os
print(os.getenv('STRIPE_SECRET_KEY'))  # Should not be None
```

---

### PAY-002: Webhook Signature Verification Failed

**Symptom:**
```
stripe.error.SignatureVerificationError
```

**Solution:**
```bash
# Use correct webhook secret
STRIPE_WEBHOOK_SECRET=whsec_...

# For local testing, use Stripe CLI
stripe listen --forward-to localhost:8000/webhooks/stripe/
```

---

## Deployment Issues

### DEP-001: Build Fails on Railway/Render

**Common Causes:**
1. Missing requirements.txt
2. Python version not specified
3. Missing Procfile

**Solution:**
```bash
# requirements.txt must exist
pip freeze > requirements.txt

# runtime.txt (specify Python version)
python-3.11.0

# Procfile
web: gunicorn soggy_potatoes.wsgi:application
```

---

### DEP-002: Static Files 404 in Production

**Solution:**
```bash
# 1. Install whitenoise
pip install whitenoise

# 2. Add to settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add after security
    ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 3. Collect static
python manage.py collectstatic
```

---

### DEP-003: Database Connection Fails in Production

**Solution:**
```python
# settings.py
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}
```

---

## Performance Issues

### PERF-001: Slow Page Loads

**Diagnosis:**
```bash
# Install Django Debug Toolbar (development only)
pip install django-debug-toolbar

# Check for N+1 queries
# Look for repeated similar queries in debug toolbar
```

**Solution:**
```python
# Use select_related for ForeignKey
products = Product.objects.select_related('category').all()

# Use prefetch_related for ManyToMany
orders = Order.objects.prefetch_related('items').all()
```

---

### PERF-002: Database Queries Too Slow

**Solution:**
```python
# Add database indexes
class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True)  # unique=True adds index

    class Meta:
        indexes = [
            models.Index(fields=['name', 'category']),
        ]
```

---

## Emergency Procedures

### Complete Reset (Development Only)

```bash
# WARNING: This deletes ALL data

# 1. Stop server
# 2. Drop and recreate database
dropdb soggy_potatoes
createdb soggy_potatoes

# 3. Delete migrations (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# 4. Recreate migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Restart server
python manage.py runserver
```

### Rollback to Last Working State

```bash
# Find last working commit
git log --oneline

# Reset to that commit
git checkout abc1234

# Or create new branch from that point
git checkout -b recovery abc1234
```

---

## Getting Help

### Before Asking for Help

1. Check this guide
2. Read the error message carefully
3. Search Stack Overflow with exact error
4. Check Django documentation

### Information to Include When Asking

```
1. Exact error message (full traceback)
2. What you were trying to do
3. What you expected to happen
4. Django version: python manage.py version
5. Python version: python --version
6. Operating system
7. Relevant code snippets
```

---

## Document Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-16 | 1.0 | Initial troubleshooting guide | Claude |

---

*End of Troubleshooting Guide*
