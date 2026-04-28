# AutoMart 2025

AutoMart is an online marketplace for automobiles across different makes, models, and body types. The platform supports private sellers and dealerships, and allows buyers to discover and purchase listed vehicles.

## Project Status
This repository currently includes:
- A Flask backend API (`backend/`) with authentication, car ads, order flows, and admin moderation endpoints.
- Static UI prototype pages (`automart/UI/`).

## Core Features Implemented
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

## API Endpoints

### Health
- `GET /` — API health check.

### Auth
- `POST /api/v1/auth/signup` — register user (supports optional admin code).
- `POST /api/v1/auth/signin` — authenticate user.

### Cars
- `POST /api/v1/car` — post a car ad (JWT required).
- `GET /api/v1/car` — list unsold cars (`min_price` / `max_price` optional query params).
- `GET /api/v1/car/<car_id>` — view a specific car ad.
- `PATCH /api/v1/car/<car_id>/status` — seller marks own ad as sold (JWT required).
- `PATCH /api/v1/car/<car_id>/price` — seller updates own ad price (JWT required).
- `DELETE /api/v1/car/<car_id>` — admin deletes an ad (JWT + admin required).

### Orders
- `POST /api/v1/order` — place purchase order for available car (JWT required).
- `PATCH /api/v1/order/<order_id>/price` — buyer updates own order offer price (JWT required).

### Admin
- `GET /api/v1/admin/car` — list all posted ads (sold and unsold) (JWT + admin required).

## Testing Coverage
The backend test suite validates:
- Authentication flows.
- Seller ad lifecycle.
- Buyer order workflow.
- Admin moderation rules.
- Authorization restrictions for protected actions.

## Author
Malcolm Mark Okabo  
Email: `malcolmmarkokabo@gmail.com`
