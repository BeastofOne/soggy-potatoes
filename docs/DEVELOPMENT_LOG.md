# Development Log

**Project:** Soggy Potatoes Sticker Shop
**Purpose:** Chronological record of all development progress, decisions, and changes

---

## How to Use This Log

- Add entries in reverse chronological order (newest at top)
- Include date, what was done, why, and any blockers
- Reference related commits when applicable
- Tag entries: `[FEATURE]`, `[FIX]`, `[CONFIG]`, `[DOCS]`, `[DECISION]`

---

## Log Entries

---

### 2026-01-16 (Phase 5)

**[FEATURE] Community Forum complete**

- Created ForumCategory model:
  - Name, slug, description, icon (Bootstrap icon class)
  - Order field for display sorting
  - Active status for moderation
  - Thread and post count helper methods
- Created Thread model:
  - Foreign key to category and author
  - Title, content, slug (auto-generated)
  - Pinned and locked flags for moderation
  - View counter (incremented on each view)
  - Score calculation (upvotes - downvotes)
- Created Post model (replies):
  - Foreign key to thread and author
  - Content field with timestamps
  - Upvote/downvote counts
  - Score calculation
- Created Reaction model:
  - Support for multiple reaction types (upvote, downvote, heart, laugh, wow)
  - Can be on thread OR post (with database constraint)
  - Unique constraint: one reaction type per user per target
  - Check constraint ensures either thread or post, not both
- Forum views implemented:
  - ForumHomeView: Categories list with thread counts, recent & popular threads
  - CategoryDetailView: Paginated thread list (20 per page)
  - ThreadDetailView: Thread with posts, view tracking, user reactions
  - CreateThreadView: New thread form with auto-first-post creation
  - create_reply: Reply submission with locked thread check
  - toggle_reaction: AJAX endpoint for upvote/downvote toggle
- Forum templates created:
  - forum/home.html - Categories grid with icons and stats
  - forum/category.html - Thread list with author, replies, views
  - forum/thread.html - Full thread view with voting buttons
  - forum/create_thread.html - New thread form
- Custom template tag:
  - forum_tags.py with `get_item` filter for dictionary lookup
- Created 4 sample forum categories:
  - General Discussion (chat-dots icon)
  - Show & Tell (camera icon)
  - Requests & Suggestions (lightbulb icon)
  - Trading & Swapping (arrow-left-right icon)
- Updated navigation:
  - Added Forum link to navbar
  - Updated home.html "Join Forum" button to link to forum

**Status:** Phase 5 - COMPLETE. Ready for Phase 6.

**Next Steps:**
1. Stripe payment integration
2. Webhook handling for payment confirmation
3. Email notifications (order confirmation)

---

### 2026-01-16 (Phase 4)

**[FEATURE] Checkout & Orders complete**

- Created CheckoutForm with shipping/contact fields:
  - Email (required, for order confirmation)
  - Phone (optional)
  - Full shipping address (name, street, city, state, zip, country)
  - Form validation for ZIP codes and email
- Checkout view with:
  - Cart validation (empty cart redirect, stock check)
  - Pre-filled user info
  - Order summary display
  - Order creation with stock reduction
  - Cart clearing after successful order
- Order confirmation page:
  - Success animation and order number display
  - Order details summary
  - Items ordered list
  - Shipping address display
  - What's next section
- Updated cart template:
  - Conditional checkout button (logged in vs guest)
  - Login redirect with next parameter
  - Register link for new users
- Free shipping (Phase 6 will add shipping calculation)
- Tax calculation placeholder (Stripe Tax in Phase 6)

**Status:** Phase 4 - COMPLETE. Ready for Phase 5.

**Next Steps:**
1. Build community forum
2. Create forum posts and threads
3. Add reactions/upvotes

---

### 2026-01-16 (Phase 3)

**[FEATURE] User Features complete**

- Created Wishlist model:
  - OneToOne relationship with User
  - ManyToMany with products
  - Toggle add/remove functionality
  - Dedicated wishlist page
- Created Review model:
  - 1-5 star rating system
  - Title and comment fields
  - Verified purchase flag (checked against orders)
  - Admin moderation support
  - One review per user per product
- Created Order and OrderItem models:
  - Full order tracking with status (pending, processing, shipped, delivered, cancelled)
  - Shipping address storage
  - Auto-generated order numbers (SP-YYYYMMDD-XXXX)
  - Stripe payment intent ID ready for Phase 6
- Enhanced product detail page:
  - Star rating display with average
  - Review count
  - Wishlist heart button
  - Customer reviews section
  - Review submission form
- Enhanced user profile:
  - Recent orders table
  - Recent reviews list
  - Wishlist link with count
  - Cart link with count
- Created new templates:
  - wishlist.html - Wishlist management
  - order_history.html - All orders
  - order_detail.html - Single order view
- Registered all new models in admin with:
  - Order management with inline items
  - Review moderation
  - Wishlist management

**Status:** Phase 3 - COMPLETE. Ready for Phase 4.

**Next Steps:**
1. Create checkout flow
2. Order confirmation emails
3. Address form validation

---

### 2026-01-16 (Phase 2)

**[FEATURE] E-Commerce Foundation complete**

- Created Product and Category models:
  - Category with slug, description, image, active status
  - Product with price, sale_price, stock, images, featured flag
  - Helper properties: current_price, is_on_sale, in_stock, discount_percent
- Cart and CartItem models:
  - User-based or session-based cart support
  - Quantity tracking and total calculations
  - Database constraints to ensure cart has user or session
- Registered all models in Django admin with:
  - Product thumbnails in list view
  - Inline cart item editing
  - Prepopulated slugs
  - List filters and search
- Product list view with:
  - Category filtering via sidebar
  - Sorting (newest, price low/high, name A-Z)
  - Pagination (12 per page)
  - Sale badges with discount percentages
- Product detail view with:
  - Breadcrumb navigation
  - Large product image
  - Sale price display with savings
  - Stock status
  - Quantity selector with stock limits
  - Related products from same category
- Shopping cart functionality:
  - Add to cart with quantity
  - Update quantities
  - Remove items
  - Subtotal calculation
  - Stock validation
- Search functionality:
  - Searches product names and descriptions
  - Uses Django Q objects for OR queries
- **Imported 99 sticker images from Sort Later folder:**
  - Created management command `import_stickers`
  - Auto-categorized: Character Sheets (11), Duo Stickers (6), Single (82)
  - Auto-priced: $5.99 (sheets), $4.99 (duos), $3.99 (singles)
  - First 6 marked as featured
  - All set to 100 stock
- Updated homepage to display real featured products

**Status:** Phase 2 - COMPLETE. Ready for Phase 3.

**Next Steps:**
1. User profile enhancements (order history)
2. Wishlist functionality
3. Product reviews

---

### 2026-01-16 (Phase 1)

**[FEATURE] Core infrastructure complete**

- Created base template with Bootstrap 5:
  - Responsive navigation with dropdowns
  - User menu (login/logout/profile)
  - Footer with social links
  - Message alerts system
- Custom CSS with purple/pink theme colors
- Homepage with:
  - Hero section with call-to-action buttons
  - Featured products grid (placeholders)
  - Features section (Made with Love, Fast Shipping, Community)
  - Newsletter signup form
- About page for Joana with:
  - Personal story section
  - Mission and quality promise
  - Contact information
- User authentication system:
  - Login view with form styling
  - Registration view
  - Logout functionality
  - Profile page with order history placeholder
- Admin panel customization (branding)
- URL routing configured for shop and users apps
- Debug toolbar enabled in development

**Commits:** `1b9fff5`

**Status:** Phase 1 - COMPLETE. Ready for Phase 2.

**Next Steps:**
1. Create Product and Category models
2. Build product listing and detail pages
3. Implement shopping cart
4. Add search functionality

---

### 2026-01-16 (continued)

**[CONFIG] Development environment setup complete**

- Installed Python 3.11 via Homebrew (system Python 3.9 was too old for Django 5.x)
- Installed PostgreSQL 16 via Homebrew
- Created Python virtual environment with Python 3.11
- Installed all dependencies:
  - Django 5.2.10
  - psycopg2-binary (PostgreSQL adapter)
  - python-dotenv (environment variables)
  - dj-database-url (database URL parsing)
  - django-crispy-forms + crispy-bootstrap5 (form styling)
  - django-cors-headers (CORS)
  - Pillow (image processing)
  - gunicorn + whitenoise (production)
  - django-debug-toolbar (development)
- Created Django project structure with 3 apps:
  - `shop/` - E-commerce functionality
  - `forum/` - Community features
  - `users/` - Authentication and profiles
- Created and configured PostgreSQL database `soggy_potatoes`
- Configured Django settings with:
  - Environment variable loading from .env
  - PostgreSQL database connection
  - Debug toolbar for development
  - WhiteNoise for static files
  - Crispy forms with Bootstrap 5
  - Security settings for production
- Created .env file with secret key and database URL
- Created .gitignore with standard Python/Django exclusions
- Ran initial migrations successfully
- Verified server starts without errors

**Blocker encountered:** System Python 3.9.6 incompatible with Django 5.x (requires 3.10+)
**Resolution:** Installed Python 3.11 via Homebrew, recreated venv

**Status:** Phase 0 - COMPLETE. Ready for Phase 1.

**Next Steps:**
1. Initialize Git repository
2. Create base templates with Bootstrap 5
3. Build homepage view
4. Set up user authentication

---

### 2026-01-16

**[DOCS] Created documentation structure**

- Created `/docs` folder with all documentation files:
  - `PROJECT_OVERVIEW.md` - Master reference document
  - `SYSTEM_OPERATIONS_MANUAL.md` - How to run/maintain
  - `TECHNICAL_PROTOCOLS.md` - Technical decisions and standards
  - `DEVELOPMENT_LOG.md` - This file
  - `TROUBLESHOOTING_GUIDE.md` - Common issues and solutions

- Converted original PDF project overview to Markdown
- Established coding standards and git workflow
- Defined database schema for shop and forum

**Status:** Phase 0 - Documentation complete, ready for environment setup

**Next Steps:**
1. Set up Python virtual environment
2. Install PostgreSQL
3. Create initial Django project
4. Begin Phase 1 development

---

### 2026-01-06

**[DECISION] Project kickoff and technology decisions**

- Project initiated for Joana's sticker shop
- Technology stack finalized:
  - Django 5.x (framework)
  - PostgreSQL 16 (database)
  - Bootstrap 5 (frontend)
  - Stripe (payments)
  - SendGrid (email)
  - Railway/Render (hosting)

- Core requirements defined:
  - E-commerce: cart, checkout, orders
  - Community: forums with reactions
  - Users: auth, profiles, order history
  - Admin: product and order management

- Primary constraint: $0 cost during development

**Status:** Phase 0 - Planning started

---

## Template for New Entries

```markdown
### YYYY-MM-DD

**[TAG] Brief description**

- What was done
- Why it was done
- Any challenges or blockers
- Related commit: `abc1234`

**Status:** Current phase/state

**Next Steps:**
1. Immediate next action
2. Following action
```

---

## Phase Progress Tracker

| Phase | Description | Status | Started | Completed |
|-------|-------------|--------|---------|-----------|
| 0 | Setup & Planning | Complete | 2026-01-06 | 2026-01-16 |
| 1 | Core Infrastructure | Complete | 2026-01-16 | 2026-01-16 |
| 2 | E-Commerce Foundation | Complete | 2026-01-16 | 2026-01-16 |
| 3 | User Features | Complete | 2026-01-16 | 2026-01-16 |
| 4 | Checkout & Orders | Complete | 2026-01-16 | 2026-01-16 |
| 5 | Community Forum | Complete | 2026-01-16 | 2026-01-16 |
| 6 | Payment Integration | Not Started | - | - |
| 7 | Polish & Testing | Not Started | - | - |
| 8 | Deployment | Not Started | - | - |

---

## Key Decisions Log

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2026-01-06 | Django 5.x | Built-in auth, admin, ORM; Python-based | Flask, FastAPI, Node.js |
| 2026-01-06 | PostgreSQL | Free, robust, cloud-compatible | SQLite, MySQL |
| 2026-01-06 | Bootstrap 5 | Rapid UI, no JS framework complexity | Tailwind, React |
| 2026-01-06 | Stripe | Best docs, automatic tax handling | PayPal, Square |
| 2026-01-06 | Railway/Render | Free tier, easy Django deploy | Heroku, DigitalOcean |

---

## Blockers & Resolutions

| Date | Blocker | Resolution | Time Lost |
|------|---------|------------|-----------|
| 2026-01-16 | System Python 3.9.6 incompatible with Django 5.x | Installed Python 3.11 via Homebrew | 5 min |

---

## Performance Notes

*Track any performance-related observations or optimizations here.*

| Date | Observation | Action Taken | Result |
|------|-------------|--------------|--------|
| - | - | - | - |

---

*End of Development Log*
