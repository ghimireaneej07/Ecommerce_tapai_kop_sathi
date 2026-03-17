from pathlib import Path
import os
from dotenv import load_dotenv

from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# SECURITY
# SECURITY: production vs development
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# Default to False for safety, only True if explicitly set to "true"
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")]
if DEBUG:
    ALLOWED_HOSTS.extend(["testserver", "0.0.0.0"])

# CSRF Trusted Origins for production (example)
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host not in ["localhost", "127.0.0.1"]]

# APPLICATIONS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "tapai_ko_sathi.core",
    "tapai_ko_sathi.apps.accounts",
    "tapai_ko_sathi.apps.products",
    "tapai_ko_sathi.apps.cart",
    "tapai_ko_sathi.apps.orders",
    "tapai_ko_sathi.apps.payments",
    "tapai_ko_sathi.apps.adminpanel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "tapai_ko_sathi.core.middleware.ErrorHandlingMiddleware",
]

ROOT_URLCONF = "tapai_ko_sathi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tapai_ko_sathi.core.context_processors.global_settings",
                "tapai_ko_sathi.apps.cart.context_processors.cart_summary",
            ],
        },
    },
]

WSGI_APPLICATION = "tapai_ko_sathi.wsgi.application"
ASGI_APPLICATION = "tapai_ko_sathi.asgi.application"


# DATABASES
# DATABASES
# Configure MySQL from environment for XAMPP/local use. Keep sensible defaults for local XAMPP.
# To use MySQL, set DB_ENGINE=django.db.backends.mysql (and other DB_* env vars).
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
    }
}

# MySQL configuration (activate by setting DB_ENGINE env var to django.db.backends.mysql)
if "mysql" in DATABASES["default"]["ENGINE"]:
    DATABASES["default"].update({
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
    })

# Provide a PyMySQL fallback on platforms where mysqlclient isn't available.
if "mysql" in DATABASES["default"]["ENGINE"]:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        
        # Monkey-patch for MySQL/MariaDB version compatibility
        from django.db.backends.mysql.base import DatabaseWrapper
        DatabaseWrapper.check_database_version_supported = lambda self: None
    except Exception:
        # If PyMySQL isn't installed, we expect `mysqlclient` to be available.
        pass

# AUTH
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

# STATIC & MEDIA
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# EMAIL
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", "no-reply@tapaikosathi.com"
)

# DJANGO REST FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

# REST Framework pagination and JWT defaults
REST_FRAMEWORK.update({
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("API_PAGE_SIZE", "12")),
})

# Simple JWT defaults (can be tuned via env)
from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Basic logging for production readiness
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "error.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
}

# SECURITY HARDENING
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_SSL_REDIRECT = False  # Enable behind HTTPS proxy
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# PAYMENT SETTINGS (environment driven)
ESEWA_MERCHANT_CODE = os.getenv("ESEWA_MERCHANT_CODE", "")
ESEWA_SUCCESS_URL = os.getenv(
    "ESEWA_SUCCESS_URL", "http://localhost:8000/payments/esewa/success/"
)
ESEWA_FAILURE_URL = os.getenv(
    "ESEWA_FAILURE_URL", "http://localhost:8000/payments/esewa/failure/"
)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

