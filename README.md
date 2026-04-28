# Automart 2025

Automart 2025 is a production-ready Django automobile marketplace where users can browse, buy, and sell vehicles with modern UX and role-based workflows.

## Features
- User registration, login, logout, and profile management.
- Car listing lifecycle: create, edit, delete, search, filter, and pagination.
- Car details with inquiry form, inspection booking, and favourites.
- Seller dashboard for listings, saved cars, and inquiries.
- Admin dashboard and Django admin customization for moderation.
- Contact page and stored contact inquiries.
- PostgreSQL-ready environment configuration and whitenoise static handling.
- Custom 404 and 500 pages.

## Screenshots
- `docs/screenshots/home.png` (placeholder)
- `docs/screenshots/listings.png` (placeholder)
- `docs/screenshots/dashboard.png` (placeholder)

## Installation Guide
```bash
git clone <your-repo-url>
cd automart2025
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run the Project
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Run Tests
```bash
python manage.py test
```

## Deployment Guide (Render / Railway / PythonAnywhere)
1. Set environment variables: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `DATABASE_URL`.
2. Use `gunicorn config.wsgi:application` as start command.
3. Run collectstatic during build:
   ```bash
   python manage.py collectstatic --noinput
   python manage.py migrate
   ```
4. Configure persistent media storage (e.g., S3 or external disk) for production uploads.

## Project Structure
```
automart2025/
├── manage.py
├── requirements.txt
├── .env.example
├── config/
├── accounts/
├── cars/
├── dashboard/
├── core/
├── templates/
├── static/
└── media/
```
