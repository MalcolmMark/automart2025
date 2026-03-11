# AutoMart 2025

AutoMart is an online marketplace for automobiles across different makes, models, and body types. The platform supports private sellers and dealerships, and allows buyers to discover and purchase listed vehicles.

## Project Status
This repository currently includes:
- A Flask backend API (`backend/`) with authentication endpoints.
- Static UI prototype pages (`automart/UI/`).

## Core Features (Planned / In Scope)
- User sign up and sign in.
- Seller can post a car sale advertisement.
- Buyer can place a purchase order.
- Buyer can update the price of a purchase order.
- Seller can mark a posted ad as sold.
- Seller can update the price of a posted ad.
- Users can view a specific car.
- Users can view all unsold cars.
- Users can filter unsold cars by price range.
- Admin can delete a posted ad.
- Admin can view all posted ads (sold and unsold).

## Tech Stack
- Python 3.10+
- Flask
- Flask-JWT-Extended
- Pytest

## Getting Started

### 1) Clone the repository
```bash
git clone https://github.com/MalcolmMark/automart2025.git
cd automart2025
```

### 2) Set up backend dependencies
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Configure environment variables
```bash
export JWT_SECRET_KEY="replace-with-a-long-random-secret"
export ADMIN_SIGNUP_CODE="replace-with-admin-signup-code"
```

### 4) Run the backend
```bash
flask --app app:create_app run --debug
```

The API will be available at `http://127.0.0.1:5000`.

## Running Tests
From the `backend/` directory:
```bash
pytest -q
```

## API Endpoints (Current)
- `GET /` — health check.
- `POST /api/v1/auth/signup` — register user.
- `POST /api/v1/auth/signin` — authenticate user.

## UI Prototype
Static prototype pages are in:
- `automart/UI/`

## Author
Malcolm Mark Okabo  
Email: `malcolmmarkokabo@gmail.com`
