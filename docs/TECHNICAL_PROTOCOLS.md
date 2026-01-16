# Technical Protocols

**Project:** Soggy Potatoes Sticker Shop
**Last Updated:** January 16, 2026
**Purpose:** Technical decisions, configurations, and standards

---

## Table of Contents

1. [Architecture Decisions](#architecture-decisions)
2. [Coding Standards](#coding-standards)
3. [Database Schema](#database-schema)
4. [API Design](#api-design)
5. [Security Protocols](#security-protocols)
6. [Testing Standards](#testing-standards)
7. [Git Workflow](#git-workflow)
8. [Configuration Reference](#configuration-reference)

---

## Architecture Decisions

### ADR-001: Django as Core Framework

**Status:** Accepted
**Date:** January 6, 2026

**Context:**
Need a web framework that supports e-commerce, user authentication, and community features while being cost-effective and scalable.

**Decision:**
Use Django 5.x as the core framework.

**Rationale:**
- Built-in admin panel saves development time
- Mature ORM prevents SQL injection
- Battle-tested authentication system
- Large ecosystem of e-commerce packages
- Excellent documentation
- Python knowledge transferable to other projects

**Consequences:**
- Learning curve for Django-specific patterns
- Monolithic by default (but can be modularized)
- Server-side rendering (not SPA by default)

---

### ADR-002: PostgreSQL as Database

**Status:** Accepted
**Date:** January 6, 2026

**Context:**
Need a database that works locally and in production, handles relational data well, and is free.

**Decision:**
Use PostgreSQL 16.

**Rationale:**
- Free and open source
- Identical behavior local vs. cloud
- Superior to SQLite for concurrent users
- JSON support for flexible data
- Full-text search built in
- Industry standard

**Consequences:**
- Must install PostgreSQL locally
- Slightly more setup than SQLite
- Need to manage database service

---

### ADR-003: Bootstrap 5 for Frontend

**Status:** Accepted
**Date:** January 6, 2026

**Context:**
Need professional-looking UI without extensive frontend development time.

**Decision:**
Use Bootstrap 5 with Django templates (server-side rendering).

**Rationale:**
- Rapid UI development
- Mobile-responsive out of box
- No JavaScript framework complexity
- Better SEO than SPA
- Can add React/Vue later if needed

**Consequences:**
- Less interactive than SPA
- Bootstrap "look" unless customized
- Page reloads for navigation

---

### ADR-004: Modular Django Apps

**Status:** Accepted
**Date:** January 6, 2026

**Context:**
Need organized code structure that allows independent development of features.

**Decision:**
Separate Django apps for each major feature:
- `shop` - E-commerce functionality
- `forum` - Community features
- `users` - Authentication and profiles

**Rationale:**
- Clear separation of concerns
- Can disable features independently
- Easier to test in isolation
- Reusable in other projects

**Consequences:**
- More files to manage
- Need clear interfaces between apps
- Potential for circular imports (avoidable)

---

## Coding Standards

### Python Style Guide

Follow PEP 8 with these project-specific additions:

```python
# Imports: Standard library, third-party, local (blank line between groups)
import os
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from shop.utils import calculate_total


# Class naming: PascalCase
class ProductCategory(models.Model):
    pass


# Function naming: snake_case
def get_product_by_slug(slug):
    pass


# Constants: UPPER_SNAKE_CASE
MAX_CART_ITEMS = 100
DEFAULT_PAGE_SIZE = 20


# Line length: 88 characters (Black formatter default)
# Use Black for auto-formatting: black .
```

### Django-Specific Standards

```python
# Models: Singular names, explicit verbose_name
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Product Name")
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})


# Views: Class-based for complex logic, function-based for simple
class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 20


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product_detail.html', {'product': product})


# URLs: Named URLs, app namespaces
app_name = 'shop'
urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
]
```

### Template Standards

```html
<!-- Base template inheritance -->
{% extends 'base.html' %}

{% load static %}

{% block title %}Page Title - Soggy Potatoes{% endblock %}

{% block content %}
<div class="container">
    <!-- Use Bootstrap classes -->
    <div class="row">
        <div class="col-md-8">
            <!-- Content here -->
        </div>
    </div>
</div>
{% endblock %}

<!-- Naming: snake_case for templates -->
<!-- shop/product_list.html -->
<!-- shop/product_detail.html -->
<!-- users/login.html -->
```

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Python modules | snake_case | `order_utils.py` |
| Templates | snake_case | `product_detail.html` |
| Static CSS | kebab-case | `main-styles.css` |
| Static JS | kebab-case | `cart-handler.js` |
| Images | kebab-case | `logo-dark.png` |

---

## Database Schema

### Core Models

```
┌─────────────────┐     ┌─────────────────┐
│     User        │     │    Category     │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ username        │     │ name            │
│ email           │     │ slug            │
│ password        │     │ description     │
│ first_name      │     │ image           │
│ last_name       │     └─────────────────┘
│ date_joined     │              │
└─────────────────┘              │
        │                        │
        │                        ▼
        │              ┌─────────────────┐
        │              │    Product      │
        │              ├─────────────────┤
        │              │ id (PK)         │
        │              │ category_id(FK) │
        │              │ name            │
        │              │ slug            │
        │              │ description     │
        │              │ price           │
        │              │ stock           │
        │              │ image           │
        │              │ is_active       │
        │              │ created_at      │
        │              └─────────────────┘
        │                        │
        ▼                        │
┌─────────────────┐              │
│     Order       │              │
├─────────────────┤              │
│ id (PK)         │              │
│ user_id (FK)    │◄─────────────┘
│ status          │
│ total           │
│ shipping_addr   │
│ created_at      │
│ updated_at      │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│   OrderItem     │
├─────────────────┤
│ id (PK)         │
│ order_id (FK)   │
│ product_id (FK) │
│ quantity        │
│ price_at_time   │
└─────────────────┘
```

### Forum Models

```
┌─────────────────┐     ┌─────────────────┐
│ ForumCategory   │     │     Thread      │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │────▶│ id (PK)         │
│ name            │     │ category_id(FK) │
│ slug            │     │ author_id (FK)  │
│ description     │     │ title           │
└─────────────────┘     │ created_at      │
                        │ is_pinned       │
                        │ is_locked       │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │      Post       │
                        ├─────────────────┤
                        │ id (PK)         │
                        │ thread_id (FK)  │
                        │ author_id (FK)  │
                        │ content         │
                        │ created_at      │
                        │ updated_at      │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Reaction      │
                        ├─────────────────┤
                        │ id (PK)         │
                        │ post_id (FK)    │
                        │ user_id (FK)    │
                        │ reaction_type   │
                        └─────────────────┘
```

### Order Status Flow

```
PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
    │         │            │           │
    └─────────┴────────────┴───────────┴──────→ CANCELLED
```

---

## API Design

### URL Structure

```
# Shop URLs
/                           # Homepage
/shop/                      # Product listing
/shop/category/<slug>/      # Category products
/shop/product/<slug>/       # Product detail
/shop/search/               # Search results
/cart/                      # Shopping cart
/cart/add/<product_id>/     # Add to cart (POST)
/cart/remove/<item_id>/     # Remove from cart (POST)
/checkout/                  # Checkout process
/orders/                    # Order history
/orders/<order_id>/         # Order detail

# Forum URLs
/forum/                     # Forum home
/forum/category/<slug>/     # Category threads
/forum/thread/<id>/         # Thread detail
/forum/thread/new/          # Create thread (POST)
/forum/post/<id>/react/     # Add reaction (POST)

# User URLs
/account/                   # User dashboard
/account/login/             # Login
/account/logout/            # Logout
/account/register/          # Registration
/account/profile/           # Edit profile
/account/password/reset/    # Password reset

# Admin URLs
/admin/                     # Django admin
```

### Response Patterns

```python
# Success responses
return render(request, 'template.html', {'data': data})
return redirect('shop:product_list')
return JsonResponse({'status': 'success', 'data': data})

# Error handling
from django.http import Http404
raise Http404("Product not found")

# Form validation
if form.is_valid():
    form.save()
    messages.success(request, "Product added successfully!")
    return redirect('shop:product_list')
else:
    messages.error(request, "Please correct the errors below.")
```

---

## Security Protocols

### Authentication

```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Session security
SESSION_COOKIE_SECURE = True  # Production only
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Login requirements
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/'
```

### CSRF Protection

```python
# Enabled by default in Django
# In templates, always use:
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>

# For AJAX requests:
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
fetch(url, {
    method: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    body: data
});
```

### Input Validation

```python
# Always use Django forms for validation
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be positive")
        return price

# Never use raw SQL
# BAD: cursor.execute(f"SELECT * FROM products WHERE id = {user_input}")
# GOOD: Product.objects.filter(id=product_id)
```

### Secret Management

```python
# .env file (NEVER commit)
SECRET_KEY=django-insecure-abc123...
DATABASE_URL=postgres://...
STRIPE_SECRET_KEY=sk_test_...

# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

---

## Testing Standards

### Test Structure

```
tests/
├── __init__.py
├── test_models.py      # Model tests
├── test_views.py       # View tests
├── test_forms.py       # Form tests
└── factories.py        # Test data factories
```

### Test Examples

```python
# tests/test_models.py
from django.test import TestCase
from shop.models import Product, Category

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Stickers",
            slug="stickers"
        )
        self.product = Product.objects.create(
            name="Test Sticker",
            slug="test-sticker",
            price=3.99,
            category=self.category,
            stock=10
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Sticker")
        self.assertEqual(self.product.price, 3.99)

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Sticker")

    def test_product_in_stock(self):
        self.assertTrue(self.product.stock > 0)


# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse

class ProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_product_list_view(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')
```

### Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test shop

# Specific test class
python manage.py test shop.tests.test_models.ProductModelTest

# With coverage
pip install coverage
coverage run manage.py test
coverage report
coverage html  # Creates htmlcov/index.html
```

---

## Git Workflow

### Branch Strategy

```
main                    # Production-ready code
├── develop             # Integration branch
│   ├── feature/cart    # Feature branches
│   ├── feature/forum
│   └── feature/auth
└── hotfix/bug-123      # Emergency fixes
```

### Commit Messages

```bash
# Format: type(scope): description

# Types:
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Formatting (no code change)
refactor: Code restructuring
test:     Adding tests
chore:    Maintenance

# Examples:
git commit -m "feat(shop): add product search functionality"
git commit -m "fix(cart): correct quantity calculation"
git commit -m "docs: update API endpoints in README"
git commit -m "test(forum): add post creation tests"
```

### Git Commands Reference

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# Save work
git add .
git commit -m "feat(scope): description"

# Update from develop
git fetch origin
git rebase origin/develop

# Push feature
git push origin feature/new-feature

# After PR merge, clean up
git checkout develop
git pull origin develop
git branch -d feature/new-feature
```

### .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Django
*.log
local_settings.py
db.sqlite3
media/

# Environment
.env
.env.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/

# Build
staticfiles/
*.egg-info/
dist/
build/
```

---

## Configuration Reference

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-xyz...` |
| `DEBUG` | Debug mode | `True` or `False` |
| `DATABASE_URL` | PostgreSQL connection | `postgres://user:pass@host:5432/db` |
| `ALLOWED_HOSTS` | Allowed domains | `localhost,127.0.0.1` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_HOST` | SMTP server | `smtp.sendgrid.net` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | SMTP username | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | - |
| `STRIPE_PUBLIC_KEY` | Stripe public key | - |
| `STRIPE_SECRET_KEY` | Stripe secret key | - |
| `AWS_ACCESS_KEY_ID` | AWS key (for S3) | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret | - |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket | - |

### Django Settings by Environment

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | `True` | `False` |
| `SECRET_KEY` | Can be simple | Must be secure |
| `ALLOWED_HOSTS` | `['localhost']` | `['soggypotatoes.com']` |
| `SECURE_SSL_REDIRECT` | `False` | `True` |
| `SESSION_COOKIE_SECURE` | `False` | `True` |
| `CSRF_COOKIE_SECURE` | `False` | `True` |

---

## Document Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-16 | 1.0 | Initial technical protocols | Claude |

---

*End of Technical Protocols*
