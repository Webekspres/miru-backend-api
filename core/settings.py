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
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
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

LANGUAGE_CODE = 'id'

TIME_ZONE = 'Asia/Jayapura'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'api.User'

CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS')
if cors_origins:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_origins.split(',') if o.strip()]

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
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'MIRU Bank Sampah API',
    'DESCRIPTION': (
        'REST API untuk sistem MIRU Bank Sampah, Distrik Mimika Baru. '
        'Semua response menggunakan JSON Envelope (`success`, `status_code`, `message`, `data`, `meta`). '
        'Panduan alur per role: `/api/guide/`. '
        'Akun demo (setelah `seed_data`): `admin/admin123`, `nasabah001/nasabah123`, '
        '`petugas1/petugas123`, `koordinator/koordinator123`.'
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
