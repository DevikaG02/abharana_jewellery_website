# Abharana: database-connected website

This package connects the existing Abharana frontend to the existing FastAPI + SQLAlchemy database. It keeps the current visual design.

## What is connected
- Admin login and protected admin product CRUD use the `admins` and `products` database tables.
- Admin image upload stores files in `abharana_backend/uploads` and saves the returned image URL in the product row.
- Homepage and Collections page fetch active products from `GET /api/products`.
- The existing curated product cards remain visible if the database has no products or the API is temporarily unavailable.
- Admin registration calls `POST /api/admin/register` and requires the private `ADMIN_REGISTRATION_KEY`.

## Run locally (Windows)
1. Keep `Abharana_frontend` and `abharana_backend` as sibling folders.
2. In `abharana_backend`, create/activate a virtual environment and install requirements:
   `py -m venv .venv`
   `.venv\Scripts\activate`
   `pip install -r requirements.txt`
3. Create `.env` from `.env.example`; set a unique `ADMIN_PASSWORD`, a persistent random `SECRET_KEY` (32+ characters), and a private `ADMIN_REGISTRATION_KEY` (16+ characters). Do not upload `.env`.
4. Start API from `abharana_backend`: `python -m uvicorn main:app --reload`.
5. Open the frontend using Live Server from `Abharana_frontend/index.html`. API config is in `Abharana_frontend/js/config.js` and defaults to `http://127.0.0.1:8000`.
6. Open `http://127.0.0.1:8000/docs` to inspect the API.

## Add products
Sign in at `/admin.html`, add a product, and upload its image. The product is saved to SQLite. It should then appear on the homepage and Collections page.

## Deploy
- Deploy `Abharana_frontend` as the Netlify publish directory.
- Deploy `abharana_backend` to a Python-compatible host. Set environment variables on that host; do not deploy `.env`.
- Change `window.ABHARANA_API_URL` in `Abharana_frontend/js/config.js` to the deployed HTTPS API base URL (no trailing slash).
- Set backend `CORS_ORIGINS` to the exact Netlify site URL (and any custom domain).
- For production, use a managed persistent database (e.g. PostgreSQL) and persistent object/file storage for uploaded images. Local SQLite and the local `uploads` folder are not durable on many cloud hosts.

## Scope
This connects the product catalogue and admin product data to the database. The current storefront uses WhatsApp enquiry links; this does not add cart, checkout, online payments, customer accounts, or order management.
