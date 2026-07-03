# 02 — Architecture & Tech Stack (Backend)

## Tech Stack

| Komponen | Teknologi | Versi |
|----------|-----------|-------|
| Framework | Django | 5.2.15 |
| REST API | Django REST Framework (DRF) | 3.17.1 |
| Auth | djangorestframework-simplejwt | 5.5.1 |
| Filtering | django-filter | 25.2 |
| CORS | django-cors-headers | 4.9.0 |
| Database | PostgreSQL 15 (via psycopg2-binary) | 2.9.12 |
| SQLite fallback | SQLite (jika USE_POSTGRES=False) | Built-in |
| API Docs | drf-spectacular (OpenAPI/Swagger) | 0.28.0 |
| Container | Docker + docker-compose | - |

## Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│                    Django REST API                       │
│                                                          │
│  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │   Viewsets   │──│Serializers│──│     Models       │   │
│  │ (Permissions)│  │(Validasi) │  │ (ORM + Indices)  │   │
│  └──────┬───────┘  └──────────┘  └────────┬─────────┘   │
│         │                                  │            │
│  ┌──────┴───────┐               ┌─────────┴─────────┐  │
│  │  URL Router  │               │    PostgreSQL      │  │
│  │  (Default    │               │   (atau SQLite)    │  │
│  │   Router)    │               └───────────────────┘  │
│  └──────────────┘                                       │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  JWT Auth    │  │  drf-        │  │  django-     │  │
│  │(simplejwt)   │  │  spectacular │  │  filter      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
         ▲                                ▲
         │ HTTP (JSON)                    │ HTTP (JSON)
         │                                │
┌────────┴────────┐          ┌───────────┴──────────┐
│   Web Admin     │          │ Mobile App Nasabah   │
│  (Next.js)      │          │    (Flutter)         │
└─────────────────┘          └──────────────────────┘
```

## Struktur Folder

```
miru-backend-api/
├── .ai-steering/           # Dokumentasi AI (file ini)
├── .env.example            # Template environment variables
├── manage.py               # Django CLI
├── requirements.txt        # Dependencies
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker services (db + web)
│
├── core/                   # Konfigurasi Django
│   ├── settings.py         # Settings (DB, JWT, CORS, DRF)
│   ├── urls.py             # Root URL config
│   ├── asgi.py             # ASGI entry point
│   └── wsgi.py             # WSGI entry point
│
└── api/                    # Aplikasi utama
    ├── models.py           # Semua model database
    ├── serializers.py      # DRF serializers
    ├── views.py            # ViewSets
    ├── urls.py             # API routes (DefaultRouter)
    ├── permissions.py      # Custom permissions
    ├── admin.py            # Django admin config
    ├── tests.py            # Unit tests
    └── migrations/         # Database migrations
```

## Environment Variables (`.env`)

```
USE_POSTGRES=True
DB_NAME=miru
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://admin.mirubanksampah.id
```

## CORS Configuration
- Selama development: `CORS_ALLOW_ALL_ORIGINS=True` (sudah default di settings.py)
- Production: set `CORS_ALLOWED_ORIGINS` dengan domain web admin dan origin mobile app

## API Documentation
- Swagger UI: `http://localhost:8000/api/docs/` (via drf-spectacular)
- OpenAPI JSON: `http://localhost:8000/api/schema/`
