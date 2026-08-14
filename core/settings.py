import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-only-change-in-production',
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

_allowed_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'api.middleware.RequestIdMiddleware',
    'api.middleware.CurrentRequestMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Monitoring: request logging JSON + spike detection (Fase 7.4)
    'api.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

if os.environ.get('USE_POSTGRES') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'miru'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            # Persistent connections — mengurangi overhead koneksi baru per request
            'CONN_MAX_AGE': int(os.environ.get('CONN_MAX_AGE', '300')),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            # SQLite: jangan cache koneksi (0) untuk hindari 'database is locked' di dev
            'CONN_MAX_AGE': int(os.environ.get('CONN_MAX_AGE', '0')),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Fast password hasher for tests to drastically speed up CI execution
if 'test' in sys.argv or os.environ.get('CI') == 'true':
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

LANGUAGE_CODE = 'id'

TIME_ZONE = 'Asia/Jayapura'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'api.User'

# ---------------------------------------------------------------------------
# CORS — Production-hardened
# ---------------------------------------------------------------------------
# Default behaviour:
#   DEBUG=True  → allow all origins (developer convenience)
#   DEBUG=False → whitelist only; env *must* set CORS_ALLOWED_ORIGINS
_cors_allow_all = os.environ.get('CORS_ALLOW_ALL_ORIGINS')
if _cors_allow_all is not None:
    CORS_ALLOW_ALL_ORIGINS = _cors_allow_all == 'True'
else:
    CORS_ALLOW_ALL_ORIGINS = bool(DEBUG)

cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS')
if cors_origins:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_origins.split(',') if o.strip()]
elif not CORS_ALLOW_ALL_ORIGINS and not DEBUG:
    # Production fallback — hard-coded whitelist prevents lockout
    CORS_ALLOWED_ORIGINS = [
        'https://admin.mirubanksampah.id',
        'https://mirubanksampah.id',
    ]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.utils.pagination.MiruPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'api.utils.renderers.EnvelopeJSONRenderer',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'api.utils.exception_handler.miru_exception_handler',
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
    # ------------------------------------------------------------------ #
    # Rate limiting (Fase 7.1)
    # ------------------------------------------------------------------ #
    # Login endpoint dilindungi oleh LoginAnonRateThrottle secara terpisah
    'DEFAULT_THROTTLE_CLASSES': [
        'api.throttles.WriteUserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/minute',   # AnonRateThrottle untuk /api/auth/login/
        'write': '100/hour',    # UserRateThrottle untuk semua write operation
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ---------------------------------------------------------------------------
# Logging — structured JSON + PII redaction (Fase 7.4)
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'pii_redact': {
            '()': 'api.logging_filters.PIIRedactFilter',
        },
    },
    'formatters': {
        'json': {
            '()': 'api.logging_filters.JSONFormatter',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console_json': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'filters': ['pii_redact'],
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['pii_redact'],
        },
    },
    'loggers': {
        # Request logger — semua request HTTP dicatat oleh middleware
        'miru.request': {
            'handlers': ['console_json'],
            'level': 'INFO',
            'propagate': False,
        },
        # Django default logger
        'django': {
            'handlers': ['console_json'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'handlers': ['console_json'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console_json'],
            'level': 'INFO',
            'propagate': False,
        },
        # Security-related events
        'django.security': {
            'handlers': ['console_json'],
            'level': 'WARNING',
            'propagate': False,
        },
        # DRF
        'rest_framework': {
            'handlers': ['console_json'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    # Root logger — fallback
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}


# ---------------------------------------------------------------------------
# Email (SMTP) — Fase 8.6: transactional admin emails
# Semua kredensial dari environment; tidak ada fallback (harus diisi di .env)
# ---------------------------------------------------------------------------
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    DEFAULT_FROM_EMAIL = os.environ.get(
        'DEFAULT_FROM_EMAIL',
        'MIRU Bank Sampah <noreply@mirubanksampah.id>',
    )
    # Admin email tujuan untuk notifikasi operasional (penjemputan baru, dll.)
    ADMIN_NOTIF_EMAIL = os.environ.get('ADMIN_NOTIF_EMAIL', '')
else:
    # Dev fallback — cetak email ke console (tidak benar-benar dikirim)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ---------------------------------------------------------------------------
# Firebase Cloud Messaging (FCM) — Fase 8.6
# Kredensial service account HANYA dari env / file di luar repo.
# ---------------------------------------------------------------------------
FCM_ENABLED = os.environ.get('FCM_ENABLED', 'False') == 'True'
# Path absolut/relatif ke file JSON service account, ATAU…
FIREBASE_CREDENTIALS_FILE = os.environ.get('FIREBASE_CREDENTIALS_FILE', '')
# …inline JSON string (berguna di CI / secret manager; jangan commit).
FIREBASE_CREDENTIALS_JSON = os.environ.get('FIREBASE_CREDENTIALS_JSON', '')


# ---------------------------------------------------------------------------
# Static & Media files (production)
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------------------------------------------------------
# Security settings — aktif hanya saat DEBUG=False (production)
# ---------------------------------------------------------------------------
if not DEBUG:
    # HTTPS via Nginx reverse proxy
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True

    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS — mulai dengan durasi pendek, naikkan setelah stabil
    SECURE_HSTS_SECONDS = 31536000  # 1 tahun
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Mencegah jenis serangan content-type sniffing
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Mencegah clickjacking
    X_FRAME_OPTIONS = 'DENY'


SPECTACULAR_SETTINGS = {
    'TITLE': 'MIRU Bank Sampah API',
    'DESCRIPTION': (
        'Selamat datang di dokumentasi REST API **MIRU Bank Sampah** (Distrik Mimika Baru).\n\n'
        '## Cara memakai dokumentasi ini\n\n'
        '1. **Authorize** — klik tombol **Authorize** di kanan atas. \n'
        '2. **Login** — buka `POST /api/auth/login/`, isi username & password, **Execute**.\n'
        '3. **Salin token** — dari response, ambil `data.access`.\n'
        '4. **Tempel token** — di dialog Authorize isi `Bearer <access_token>` '
        '(atau hanya token jika UI sudah menambah prefix `Bearer`).\n'
        '5. **Uji endpoint** — pilih operasi, **Try it out** → **Execute**. '
        'Endpoint terlindungi akan memakai token yang sudah disimpan.\n\n'
        '## Format response\n\n'
        'Semua JSON memakai envelope: '
        '`success`, `status_code`, `message`, `data`, `meta`.\n\n'
        '## Dokumen terkait\n\n'
        '- Panduan alur per role (onboarding): [`/api/guide/`](/api/guide/)\n'
        '- Schema OpenAPI mentah: [`/api/schema/`](/api/schema/)\n'
        '- ReDoc: [`/api/redoc/`](/api/redoc/)\n\n'
        '## Akun demo (setelah `python manage.py seed_data`)\n\n'
        '| Role | Username | Password |\n'
        '|---|---|---|\n'
        '| admin | `admin` | `admin123` |\n'
        '| koordinator | `koordinator` | `koordinator123` |\n'
        '| petugas | `petugas1` | `petugas123` |\n'
        '| pemerintah | `pemerintah` | `pemerintah123` |\n'
        '| nasabah | `nasabah001` | `nasabah123` |\n'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'TAGS': [
        {'name': 'Auth', 'description': 'Login JWT, refresh token, dan profil user.'},
        {'name': 'Health', 'description': 'Status server.'},
        {'name': 'Users', 'description': 'Registrasi nasabah dan manajemen pengguna.'},
        {'name': 'Waste Categories', 'description': 'Kategori sampah dan harga beli per kg.'},
        {'name': 'Deposits', 'description': 'Transaksi setoran sampah.'},
        {'name': 'Pickups', 'description': 'Penjemputan sampah dari nasabah.'},
        {'name': 'Withdrawals', 'description': 'Penarikan saldo nasabah.'},
        {'name': 'Rewards', 'description': 'Katalog reward penukaran poin.'},
        {'name': 'Reward Redemptions', 'description': 'Penukaran poin nasabah.'},
        {'name': 'Partners', 'description': 'Mitra pengepul sampah.'},
        {'name': 'Partner Sales', 'description': 'Penjualan stok ke mitra.'},
        {'name': 'Complaints', 'description': 'Pengaduan nasabah.'},
        {'name': 'Notifications', 'description': 'Notifikasi in-app.'},
        {'name': 'Activity', 'description': 'Activity feed transaksi/poin.'},
        {'name': 'Dashboard', 'description': 'Ringkasan monitoring.'},
        {'name': 'Reports', 'description': 'Laporan periode.'},
        {'name': 'Inventory', 'description': 'Stok gudang.'},
        {'name': 'Audit Log', 'description': 'Riwayat perubahan data untuk audit (admin only).'},
        {'name': 'Settings', 'description': 'Pengaturan institusi dan pengumuman.'},
    ],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'Token dari `POST /api/auth/login/`. Format: `Bearer <access_token>`',
            },
        },
    },
    'SECURITY': [{'BearerAuth': []}],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'filter': True,
    },
}
