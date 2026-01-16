# Deployment Guide

This guide covers deploying Soggy Potatoes to production hosting platforms.

## Quick Start

1. Choose a hosting platform (Railway or Render recommended)
2. Connect your GitHub repository
3. Configure environment variables
4. Deploy!

---

## Option 1: Railway (Recommended)

Railway offers a generous free tier and easy Django deployment.

### Steps

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `soggy-potatoes` repository

3. **Add PostgreSQL Database**
   - Click "New" in your project
   - Select "Database" > "PostgreSQL"
   - Railway will auto-configure `DATABASE_URL`

4. **Configure Environment Variables**
   - Click on your app service
   - Go to "Variables" tab
   - Add the following:

   ```
   DEBUG=False
   SECRET_KEY=<generate-new-key>
   ALLOWED_HOSTS=your-app.railway.app
   STRIPE_PUBLIC_KEY=pk_live_xxx
   STRIPE_SECRET_KEY=sk_live_xxx
   STRIPE_WEBHOOK_SECRET=whsec_xxx
   STRIPE_LIVE_MODE=True
   ```

   Generate a secret key:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Deploy**
   - Railway will auto-detect Django and deploy
   - The `Procfile` handles migrations and static files

6. **Create Admin User**
   - Go to Railway's terminal (click "Command Palette" > "Open Shell")
   - Run: `python manage.py createsuperuser`

7. **Custom Domain (Optional)**
   - Go to Settings > Domains
   - Add your custom domain
   - Configure DNS with provided CNAME

---

## Option 2: Render

Render is another excellent free option.

### Steps

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New" > "Web Service"
   - Connect your GitHub repo
   - Select `soggy-potatoes`

3. **Configure Service**
   - **Name**: soggy-potatoes
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn soggy_potatoes.wsgi`

4. **Add PostgreSQL Database**
   - Click "New" > "PostgreSQL"
   - Copy the Internal Database URL

5. **Set Environment Variables**
   - In Web Service settings, add:

   ```
   DEBUG=False
   SECRET_KEY=<generate-new-key>
   ALLOWED_HOSTS=your-app.onrender.com
   DATABASE_URL=<paste-internal-db-url>
   PYTHON_VERSION=3.11.7
   STRIPE_PUBLIC_KEY=pk_live_xxx
   STRIPE_SECRET_KEY=sk_live_xxx
   STRIPE_WEBHOOK_SECRET=whsec_xxx
   STRIPE_LIVE_MODE=True
   ```

6. **Deploy**
   - Render will build and deploy automatically

---

## Stripe Configuration

### Get API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Publishable key** (`pk_live_xxx`)
3. Copy your **Secret key** (`sk_live_xxx`)

### Set Up Webhooks

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter your webhook URL: `https://yourdomain.com/webhook/stripe/`
4. Select events:
   - `checkout.session.completed`
   - `payment_intent.payment_failed`
5. Copy the **Webhook signing secret** (`whsec_xxx`)

### Test Webhooks Locally (Optional)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/webhook/stripe/
```

---

## Email Configuration (SendGrid)

1. **Create SendGrid Account**
   - Go to [sendgrid.com](https://sendgrid.com)
   - Create a free account

2. **Create API Key**
   - Go to Settings > API Keys
   - Create an API key with "Mail Send" permission
   - Copy the key (shown only once!)

3. **Set Environment Variables**
   ```
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=<your-api-key>
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com
   ```

4. **Verify Sender Identity**
   - Go to Settings > Sender Authentication
   - Verify your domain or single sender email

---

## Post-Deployment Checklist

- [ ] Site loads without errors
- [ ] Can create admin account
- [ ] Can register new users
- [ ] Can browse products
- [ ] Can add items to cart
- [ ] Checkout works (test with Stripe test mode first!)
- [ ] Order confirmation emails send
- [ ] Forum loads correctly
- [ ] Static files (CSS, images) load correctly
- [ ] HTTPS is enabled (automatic on Railway/Render)

---

## Troubleshooting

### Static Files Not Loading

```bash
# Run on deployment platform's shell
python manage.py collectstatic --noinput
```

### Database Migrations Not Applied

```bash
# Run on deployment platform's shell
python manage.py migrate
```

### 500 Errors

1. Check logs in Railway/Render dashboard
2. Verify all environment variables are set
3. Ensure `DEBUG=False` but `ALLOWED_HOSTS` includes your domain

### Stripe Webhooks Failing

1. Verify webhook URL is correct (include trailing slash)
2. Check `STRIPE_WEBHOOK_SECRET` is set correctly
3. Ensure CSRF exemption is working (already configured)

---

## Costs

### Railway
- **Starter Plan**: $5/month (500 hours free)
- **PostgreSQL**: Included in plan
- **Hobby Plan**: $20/month (unlimited)

### Render
- **Free Tier**: Spins down after inactivity (slow cold starts)
- **Starter**: $7/month (always on)
- **PostgreSQL Free**: 90-day limit, then paid

### Stripe
- **Transaction Fee**: 2.9% + $0.30 per transaction
- **No monthly fee**

### SendGrid
- **Free Tier**: 100 emails/day
- **Paid**: Starts at $19.95/month

---

## Security Checklist

- [x] `DEBUG=False` in production
- [x] Strong `SECRET_KEY` (never commit to git)
- [x] HTTPS enabled (automatic on Railway/Render)
- [x] CSRF protection enabled
- [x] Stripe webhook signature verification
- [x] SQL injection protection (Django ORM)
- [x] XSS protection (Django templates)
- [ ] Set up database backups (platform-specific)
- [ ] Monitor error logs

---

## Updating in Production

1. Push changes to GitHub
2. Railway/Render will auto-deploy
3. Migrations run automatically via Procfile

For manual deployment:
```bash
# On deployment platform shell
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

---

*Last updated: January 2026*
