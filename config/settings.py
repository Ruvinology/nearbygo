"""
Django settings for the NearbyGo project.

Deployment-specific values (secret key, database credentials, the private
reference location, HTTPS flags) are read from environment variables or a
local .env file so that nothing sensitive is hard-coded (NFR-QA-07).
See .env.example for every supported variable.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


def env_float(name):
    value = os.environ.get(name, "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} must be a number.") from exc


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = env_bool("DJANGO_DEBUG", default=False)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-insecure-key-change-me"
    else:
        raise ImproperlyConfigured("Set DJANGO_SECRET_KEY (or DJANGO_DEBUG=True for local development).")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "places.apps.PlacesConfig",
    "planner.apps.PlannerConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "places.middleware.AdminIdleTimeoutMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "places.context_processors.site_settings",
                "planner.context_processors.plan_summary",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database: MySQL 8.0 by default (SRS 2.5). SQLite is available only as a
# convenience for a quick local trial: set DB_ENGINE=sqlite.
# ---------------------------------------------------------------------------
DB_ENGINE = os.environ.get("DB_ENGINE", "mysql").strip().lower()

if DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME", "nearbygo"),
            "USER": os.environ.get("DB_USER", "nearbygo"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            "TEST": {
                "CHARSET": "utf8mb4",
                "COLLATION": "utf8mb4_unicode_ci",
            },
        }
    }
elif DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    raise ImproperlyConfigured("DB_ENGINE must be 'mysql' or 'sqlite'.")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Authentication and passwords (NFR-SE-02: Django's one-way hashing)
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "admin:login"

# ---------------------------------------------------------------------------
# Localisation (SRS 1.2, OR-01, OR-02)
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Asia/Colombo"
USE_I18N = True
USE_TZ = True
DEFAULT_CHARSET = "utf-8"

# ---------------------------------------------------------------------------
# Static and uploaded files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# ---------------------------------------------------------------------------
# Sessions and security (IR-COM-04, NFR-SE-03, NFR-SE-06, NFR-SE-08)
# ---------------------------------------------------------------------------
# Visitor plans live as long as the browser session cookie (FR-VP-07).
SESSION_COOKIE_AGE = int(os.environ.get("SESSION_COOKIE_AGE", 60 * 60 * 24 * 7))
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Administrators are signed out after this many seconds without activity.
ADMIN_IDLE_TIMEOUT = int(os.environ.get("ADMIN_IDLE_TIMEOUT", 30 * 60))

USE_HTTPS = env_bool("USE_HTTPS", default=False)
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
SECURE_SSL_REDIRECT = USE_HTTPS
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 3600)) if USE_HTTPS else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
if env_bool("BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# NearbyGo-specific settings
# ---------------------------------------------------------------------------
NEARBYGO = {
    # BR-01 / FR-AD-07: the project radius around the private reference point.
    "RADIUS_KM": float(os.environ.get("NEARBYGO_RADIUS_KM", 25)),
    # Private reference location (NFR-SE-07). Used only server-side for the
    # straight-line radius check. Never passed to templates or JavaScript.
    "REFERENCE_LAT": env_float("NEARBYGO_REFERENCE_LAT"),
    "REFERENCE_LNG": env_float("NEARBYGO_REFERENCE_LNG"),
    # Public map centre: Panadura town centre (a public landmark, not the
    # private reference location).
    "MAP_CENTER": (6.7133, 79.9042),
    "MAP_ZOOM": 11,
    # TBD-04: tile endpoint chosen at deployment. Attribution is always shown.
    "MAP_TILE_URL": os.environ.get("MAP_TILE_URL", "https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
    "MAP_ATTRIBUTION": os.environ.get(
        "MAP_ATTRIBUTION",
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    ),
}

# ---------------------------------------------------------------------------
# Logging: errors to the console so they appear in server logs.
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "WARNING")},
}
