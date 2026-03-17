# Project Documentation

## Overview

Tapai Ko Sathi is a Django e-commerce project with modular apps for accounts, products, cart, orders, and payments.

Core project package: `tapai_ko_sathi`

## Current Structure

- `tapai_ko_sathi/apps/accounts` - authentication, profile, address, account APIs
- `tapai_ko_sathi/apps/products` - catalog, product listing/detail
- `tapai_ko_sathi/apps/cart` - guest/user cart and cart APIs
- `tapai_ko_sathi/apps/orders` - checkout and order lifecycle
- `tapai_ko_sathi/apps/payments` - payment flows and verification hooks
- `templates` - all HTML templates by feature
- `static` - source static assets

## Local Setup

1. Create local environment file:

```powershell
copy .env.example .env
```

2. Install packages:

```powershell
python -m pip install -r requirements.txt
```

3. Migrate and run:

```powershell
python manage.py migrate
python manage.py runserver
```

## Required Environment Notes

- Configure `DJANGO_SECRET_KEY` in `.env`
- Configure database values in `.env` (`DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- For production, set `DJANGO_DEBUG=False` and update allowed hosts/CSRF origins

## Key API Endpoints

- Register: `POST /api/accounts/register/`
- Token: `POST /api/accounts/token/`
- Profile: `GET /api/accounts/me/`
- Cart: `GET/POST /api/cart/`
- Cart count: `GET /api/cart/count/`
- Checkout: `POST /api/orders/api/checkout/`

## Deployment Checklist

1. Install dependencies from `requirements.txt`
2. Configure production `.env`
3. Run migrations: `python manage.py migrate`
4. Collect static: `python manage.py collectstatic --noinput`
5. Start app with production server and reverse proxy

## Notes on Cleanup

Project cleanup removed commit helper scripts, one-time migration/debug helper scripts, and redundant status/progress markdown files. This file is now the single maintained project documentation source.