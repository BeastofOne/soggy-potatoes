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
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_products
```

> ⚠️ `seed_products` replaces the old `loaddata fixtures/products.json` step (June 2026).
> The old command re-loaded the fixture on EVERY deploy, silently reverting any product
> edits Joana made (names, prices, images for products 1-99). `seed_products` only loads
> the seed fixture (now at `fixtures/products_seed.json`) when the product table is empty.
> **The Render dashboard build command should be updated by hand to match the line above**
> (or set to `./build.sh`). Until then it is harmless: `fixtures/products.json` is now an
> intentionally empty file, so the old `loaddata` step is a no-op (see fixtures/README.md).

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
│   ├── products_seed.json   # 99 products + 3 categories (loaded by seed_products)
│   └── products.json        # intentionally empty no-op (see fixtures/README.md)
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
- Configured in `settings.py` via the `STORAGES` dict (Django 5.1+ removed the old
  `DEFAULT_FILE_STORAGE`/`STATICFILES_STORAGE` settings — they were silently ignored,
  which is why uploads used to disappear on Render; fixed June 2026)
- Cloudinary public IDs must be `media/<path-without-extension>` to match the URLs
  django-cloudinary-storage generates; `sync_to_cloudinary` handles this
- Uploads are validated (JPEG/PNG/GIF/WebP, max 10MB = Cloudinary free-tier limit)

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
python manage.py seed_products
python manage.py runserver
```

---

## Useful Commands

```bash
# Create superuser
python manage.py createsuperuser

# Export products to fixture
python manage.py dumpdata shop.Category shop.Product --indent 2 > fixtures/products_seed.json

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

### June 2026 — Overhaul
- **Fixed media storage**: Django 5.2 ignores `DEFAULT_FILE_STORAGE`; switched to the
  `STORAGES` setting so Cloudinary is actually used in production (uploads previously
  went to Render's ephemeral disk and vanished on redeploy)
- **Fixed unbuyable shop**: cart/checkout/quantity dropdowns required `stock > 0` even
  for made-to-order products (`track_inventory=False`); now respect `track_inventory`
  with a per-line cap of 10 (`Product.MAX_ORDER_QUANTITY`)
- **Fixed deploy clobbering**: new `seed_products` command loads the fixture only when
  the product table is empty (Render build command must be updated by hand)
- **Synced all 99 product images to Cloudinary** under the correct `media/products/...`
  public IDs; rewrote `sync_to_cloudinary` to match the storage backend's URL scheme
- **Fixed Stripe dev-mode detection**: was comparing the secret key against a
  `pk_test_...` prefix, so placeholder keys hit real Stripe and errored at checkout
- **Added upload validation**: type/size/integrity checks (`shop/uploads.py`) on product,
  badge, avatar, and pet-photo uploads — friendly errors instead of crashes
- **Guest carts now survive login**: session cart merges into the account cart
  (`shop/signals.py`); previously items vanished when logging in at checkout
- **Login `next` redirect validated** against the request host (open-redirect fix)
- Whitenoise manifest static storage active in production only (tests/dev use plain)

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
