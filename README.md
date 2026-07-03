# MIRU Bank Sampah - Backend

Backend API for "MIRU Bank Sampah", built with Django REST Framework. Uses SQLite for local dev, PostgreSQL for staging/prod.

## Local Development (SQLite)

Local development doesn't require Docker. It uses SQLite by default.

### 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Migrations & Server
```bash
python manage.py migrate
python manage.py runserver
```

## Staging / Production (Docker + PostgreSQL)

Docker Compose is used to spin up the Django app alongside a PostgreSQL database for staging or production.

### 1. Environment Variables
Copy `.env.example` to `.env` (ensure `USE_POSTGRES=True` is set).

### 2. Build and Run
```bash
docker-compose up --build -d
```

### 3. Run Migrations in Docker
```bash
docker-compose exec web python manage.py migrate
```

## API Access

- **API Base URL**: `http://localhost:8000/api/`

### Authentication

The API uses JWT for authentication.
- Obtain Token: `POST /api/auth/login/`
- Refresh Token: `POST /api/auth/refresh/`

Pass the token in the `Authorization` header for protected endpoints:
```
Authorization: Bearer <your_access_token>
```
