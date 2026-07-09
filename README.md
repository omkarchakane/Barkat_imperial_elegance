# 🛍️ Barkat Imperial Elegance

A full-featured Django e-commerce platform built for saree retail — covering product discovery, cart, wishlist, a multi-step checkout flow, and post-purchase reviews.

🔗 Live Demo: https://barkat-imperial-elegance-e81s.onrender.com
📸 Screenshots:<img width="2550" height="1259" alt="Screenshot (213)" src="https://github.com/user-attachments/assets/eda5b97b-4c51-4d42-b16d-a41b3cab09c4" />

<img width="2543" height="1194" alt="Screenshot (216)" src="https://github.com/user-attachments/assets/41587a43-3236-40ea-9c9c-354149e14690" />


---

## Overview

Barkat Imperial Elegance is a Django monolith designed to simulate a real production e-commerce workflow — from catalog browsing to order fulfillment — with a strong focus on data integrity and clean relational database design.

## Features

- 🏠 **Dynamic homepage** with new arrivals, promotional posters, and live search
- 🖼️ **Product catalog** with multi-image galleries and related product suggestions
- ❤️ **Wishlist** with duplicate-prevention constraints
- 🛒 **Cart management** with quantity controls and live total calculation
- 📦 **3-step checkout flow** (order summary → shipping → payment) with session-based data handling
- ⭐ **Review system** with purchase-verification — only customers who received a delivered order can leave a review
- 👤 **User profiles** with order history and status tracking
- 🔐 **Session-based authentication** with hashed passwords

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2.5, Python |
| Database | PostgreSQL |
| Frontend | Bootstrap 5, Vanilla JS, GSAP (animations) |
| Media Storage | Cloudinary |
| Static Files | WhiteNoise |
| Deployment | Render, Gunicorn |
| Local Dev DB | Docker Compose (PostgreSQL container) |

## Architecture

```
Browser (Django Templates + Bootstrap + GSAP)
        ↓
Django URL Routing (shop.urls)
        ↓
View Functions (shop.views)
        ↓
Django ORM (shop.models)
        ↓
PostgreSQL Database
```

A classic Django monolith — server-rendered templates, no separate frontend framework, all business logic in view functions backed by the ORM.

## Database Design

The schema evolved iteratively across 9 migrations, starting from a basic catalog and growing into a full checkout system:

- `Product`, `ProductImage`, `OfferPoster` — catalog and promotions
- `Cart`, `Wishlist` — session-linked user actions with unique constraints
- `Review` — includes purchase-eligibility validation before a review can be created
- `Order`, `OrderItem` — created at checkout, with cascading foreign key relationships

Query performance is optimized using `prefetch_related()` and `select_related()` to minimize N+1 query issues on product galleries and order history pages.

## Getting Started

```bash
# Clone the repo
git clone https://github.com/omkarchakane/Barkat_imperial_elegance
cd barkat-imperial-elegance

# Set up local PostgreSQL via Docker
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (see .env.example)
cp .env.example .env

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

## Environment Variables

```
DB_NAME=barkat_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
CLOUDINARY_URL=your_cloudinary_url
DEBUG=True
```

## Known Improvements (Roadmap)

-  Wrap checkout order creation in `transaction.atomic()` for strict all-or-nothing writes
-  Migrate from custom `UserRegister` to Django's built-in `User` model
-  Add automated test coverage (`shop/tests.py`)
-  Add database indexes for high-frequency filters (username, order date, review lookups)
-  Switch cart/order monetary fields to `DecimalField` for currency precision
-  Add stronger server-side validation for shipping/postal inputs

## Deployment

Deployed on **Render** with:
- Automated migrations on deploy (`migrate --noinput`)
- Gunicorn as the WSGI server
- Managed PostgreSQL with SSL enforced in production
- Environment-driven configuration via `python-decouple`

---

*Built as a hands-on project to strengthen full-stack Django development, relational database design, and production deployment workflows.*
