# Soggy Potatoes - Project Documentation

## Overview
E-commerce sticker shop for Joana, built with Django. Features a community forum, user profiles, admin dashboard, and Stripe payments.

**Live URL:** https://soggy-potatoes.onrender.com

---

## Tech Stack

### Backend
- **Framework:** Django 5.x
- **Database:** PostgreSQL (Render managed)
- **Python:** 3.11+

### Frontend
- **CSS Framework:** Bootstrap 5
- **Icons:** Bootstrap Icons
- **Fonts:** Quicksand & Nunito (Google Fonts)
- **Theme:** Pastel purple aesthetic with whales, cats, and cute elements

### Hosting & Services
- **Hosting:** Render (free tier)
- **Database:** Render PostgreSQL
- **Media Storage:** Cloudinary (free tier - 25GB)
- **Uptime Monitoring:** UptimeRobot (keeps site awake)

---

## Environment Variables (Render)

```
DATABASE_URL=<auto-set by Render>
SECRET_KEY=<django secret key>
DEBUG=False
ALLOWED_HOSTS=soggy-potatoes.onrender.com
CLOUDINARY_URL=cloudinary://682639737116537:FOzuaEOPC6es6CVb6ZPIjt0sFw8@dyph2f41l
STRIPE_PUBLIC_KEY=<stripe publishable key>
STRIPE_SECRET_KEY=<stripe secret key>
```

---

## Render Configuration

**Build Command:**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py loaddata fixtures/products.json
```

**Start Command:**
```
gunicorn soggy_potatoes.wsgi:application
```

---

## Project Structure

```
soggy-potatoes/
├── soggy_potatoes/          # Main Django project
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL config
│   └── wsgi.py              # WSGI entry point
├── shop/                    # E-commerce app
│   ├── models.py            # Product, Category, Cart, Order, Review, Wishlist
│   ├── views.py             # Shop views
│   └── templates/shop/      # Shop templates
├── users/                   # User management app
│   ├── models.py            # UserProfile, PetPhoto (planned)
│   ├── views.py             # Auth, profile, admin dashboard
│   └── templates/users/     # User templates
├── forum/                   # Community forum app
│   ├── models.py            # ForumCategory, Thread, Post
│   └── templates/forum/     # Forum templates
├── templates/               # Base templates
│   └── base.html            # Main layout
├── static/                  # Static files
│   ├── css/style.css        # Main stylesheet (pastel purple theme)
│   └── img/                 # Images including favicon
├── fixtures/                # Database fixtures
│   └── products.json        # 99 products + 3 categories
├── requirements.txt         # Python dependencies
└── build.sh                 # Build script (optional)
```

---

## Key Models

### shop/models.py

**Product**
- `name`, `slug`, `description`, `price`, `sale_price`
- `image` (Cloudinary), `additional_images` (JSON)
- `stock`, `track_inventory` (if False, always shows "In Stock")
- `is_active`, `is_featured`
- `category` (FK to Category)

**Category**
- `name`, `slug`, `description`, `image`, `is_active`

**Cart / CartItem**
- Session-based or user-linked shopping cart

**Order / OrderItem**
- Customer orders with shipping info, Stripe payment

**Review**
- Product reviews with 1-5 rating

**Wishlist**
- User's saved products

### users/models.py

**UserProfile** (planned)
- Bio, location, avatar
- Pet info (names, types, photos)
- Links to forum activity

### forum/models.py

**ForumCategory**
- Forum sections (General, Art, etc.)

**Thread**
- Discussion threads with author, views, pins

**Post**
- Replies to threads

---

## Admin Features

**URL:** `/admin-dashboard/`

- Product management (CRUD)
- Category management
- Order management with status updates
- User management with badges
- Forum moderation (pin, lock, delete threads/posts)
- Setup wizard for initial configuration

**Superuser:** joana / (password set by Joana)

---

## Key Features

### Inventory System
- `track_inventory` field on Product model
- If `False` (default): Product always shows "In Stock" - ideal for made-to-order
- If `True`: Checks actual `stock` count

### Image Storage
- Uses Cloudinary when `CLOUDINARY_URL` env var is set
- Falls back to local storage in development
- Configured in `settings.py` with `django-cloudinary-storage`

### User Badges
- Stored in UserProfile or session
- Admin can assign badges to users
- Displayed on forum posts and profiles

---

## Deployment Checklist

1. Push code to GitHub
2. Render auto-deploys from main branch
3. Build command runs migrations + loads fixtures
4. Cloudinary handles media uploads
5. UptimeRobot pings every 5 minutes to prevent sleep

---

## Local Development

```bash
cd soggy-potatoes
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/products.json
python manage.py runserver
```

---

## Useful Commands

```bash
# Create superuser
python manage.py createsuperuser

# Export products to fixture
python manage.py dumpdata shop.Category shop.Product --indent 2 > fixtures/products.json

# Sync images to Cloudinary (if needed)
python manage.py sync_to_cloudinary

# Import stickers from folder
python manage.py import_stickers --source /path/to/images/
```

---

## Service Credentials

### Cloudinary
- **Cloud Name:** dyph2f41l
- **Dashboard:** https://cloudinary.com/console

### Render
- **Dashboard:** https://dashboard.render.com
- **Service:** soggy-potatoes

### UptimeRobot
- **Dashboard:** https://uptimerobot.com
- **Monitor:** HTTP(s) ping every 5 minutes

### Stripe
- **Dashboard:** https://dashboard.stripe.com
- Keys stored in Render environment variables

---

## CSS Theme (style.css)

```css
:root {
    --sp-primary: #b794f6;        /* Main purple */
    --sp-primary-light: #e9d5ff;  /* Light purple */
    --sp-primary-dark: #9f7aea;   /* Dark purple */
    --sp-secondary: #f9a8d4;      /* Pink accent */
    --sp-accent: #fef3c7;         /* Warm cream */
}
```

- Quicksand font for headings
- Nunito font for body text
- Floating decorative elements (whales, cats, stars)
- Rounded buttons and cards
- Soft shadows

---

## Recent Changes Log

### January 2025
- Added `track_inventory` field to fix "Out of Stock" issue
- Integrated Cloudinary for persistent media storage
- Created product fixtures (99 products, 3 categories)
- Aesthetic overhaul: pastel purple theme, cute fonts, whale favicon
- Added floating decorative elements to hero section
- Updated login/register pages with cute styling

---

## Planned Features

- [ ] Public user profiles with pet info
- [ ] Pet photo gallery on profiles
- [ ] Forum username links to profiles
- [ ] Email notifications for orders
- [ ] Coupon/discount system
