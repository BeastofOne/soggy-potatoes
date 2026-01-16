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
| 1 | Core Infrastructure | Not Started | - | - |
| 2 | E-Commerce Foundation | Not Started | - | - |
| 3 | User Features | Not Started | - | - |
| 4 | Checkout & Orders | Not Started | - | - |
| 5 | Community Forum | Not Started | - | - |
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
