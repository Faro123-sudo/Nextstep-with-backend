"""
Django settings for nextstep project.

This file centralizes configuration. Important operational notes:

- Keep secret values in the environment (.env used in development).
- `SECRET_KEY`, `EMAIL_HOST_PASSWORD`, `GEMINI_API_KEY` must be set in
    production — the app will fallback to safe development defaults where
    possible but will not be secure without them.
- `rest_framework_simplejwt.token_blacklist` is enabled; run migrations
    after pulling changes: `python manage.py migrate`.
- Throttling scopes (`auth`, `ai`) are defined here to protect sensitive
    endpoints; tune rates for production traffic.

See README for deployment checklist.
"""

from pathlib import Path
import os
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    "corsheaders",
    'rest_framework_simplejwt.token_blacklist',
    'core',
    'accounts',
    'ai',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",  # Should be placed high, before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings for credentialed requests (cookies)

# --- HTTPS/Production Security Settings (Disabled for Local Development) ---
# In production, you would uncomment these lines.
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    )
}

# Throttling to protect auth and AI endpoints from abuse
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_CLASSES", [
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
    "rest_framework.throttling.ScopedRateThrottle",
])
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_RATES", {
    # reasonable defaults for development; tune in production
    "anon": "100/day",
    "user": "1000/day",
    # you can add scoped rates like 'ai': '30/min' and set throttle_scope on views
    "ai": "30/min",
    "auth": "60/min",
})

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=300),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
REST_FRAMEWORK["DEFAULT_FILTER_BACKENDS"] = [
    "django_filters.rest_framework.DjangoFilterBackend",
    "rest_framework.filters.SearchFilter",
    "rest_framework.filters.OrderingFilter",
]


ROOT_URLCONF = 'nextstep.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nextstep.wsgi.application'



# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
AUTH_USER_MODEL = "accounts.User"


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost",
]

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}

JAZZMIN_SETTINGS ={
    "site_title": "NextStep Admin",
    "site_header": "NextStep ",
    "site_brand": "NextStep",
    # show_ui_builder should be set to False in production
    "show_ui_builder" : True,
    "copyright": "NextStep Ltd",
    "site_logo_classes": "img-circle",
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Frontend URL used to construct links in emails
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Default from email fallback for development
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# Email Configuration for SendGrid
# In production, use environment variables for sensitive data like EMAIL_HOST_PASSWORD.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'apikey'  # This is the literal username for SendGrid API keys.
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# For development, you can print emails to the console instead of sending them
# by uncommenting the following line:
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ---------------------------------------------------------------------------
# Cache configuration
# ---------------------------------------------------------------------------
# Uses local-memory cache in development (no external dependencies).
# For production, switch to Redis:
#   CACHES = {
#       "default": {
#           "BACKEND": "django.core.cache.backends.redis.RedisCache",
#           "LOCATION": "redis://127.0.0.1:6379/1",
#       }
#   }
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "nextstep-cache",
        "TIMEOUT": 86400,  # 24-hour default TTL
    }
}

# Per-scope cache TTLs (seconds)
AI_CACHE_TTL = {
    "quiz_recommendation": 86400,    # 24h
    "career_detail": 86400,          # 24h
    "career_search": 3600,           # 1h — search results may change
    "resource_library": 21600,       # 6h — curated lists stay useful longer
    "resource_search": 3600,         # 1h — search is query-specific
}