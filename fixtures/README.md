# Fixtures

- `products_seed.json` — the real seed data (99 products + 3 categories). Loaded by
  `python manage.py seed_products`, which only runs `loaddata` when the product table
  is empty, so live product edits are never overwritten.
- `products.json` — intentionally an empty list. The Render dashboard's build command
  still runs `loaddata fixtures/products.json` on every deploy; keeping this file as a
  no-op makes that step harmless until the dashboard command is updated to
  `python manage.py seed_products`. Do not put data back in this file.
