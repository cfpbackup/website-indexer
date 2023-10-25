"""
Django settings for viewer project.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-a94cjadrz=y0o+c75138ro=gn3oq0*by)gs1cs88k$9+taepp("

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "debug_toolbar",
    "django.contrib.humanize",
    "django.contrib.staticfiles",
    "django_filters",
    "rest_framework",
    "crawler",
    "viewer",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "viewer.context_processors.crawl_stats",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

_sample_db_path = str(BASE_DIR / "sample" / "sample.sqlite3")
_env_db_path = os.getenv("CRAWL_DATABASE")

if _env_db_path and os.path.exists(_env_db_path) and "test" not in sys.argv:
    CRAWL_DATABASE = _env_db_path
else:
    CRAWL_DATABASE = _sample_db_path

_sqlite_db_path = f"file:{CRAWL_DATABASE}?mode=ro"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _sqlite_db_path,
        "TEST": {
            "NAME": _sqlite_db_path,
            "MIGRATE": False,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ALLOWED_HOSTS = ["*"]

# django-debug-toolbar
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_COLLAPSED": True,
}

# django-rest-framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "viewer.pagination.BetterPageNumberPagination",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework_csv.renderers.CSVStreamingRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "PAGE_SIZE": 25,
    "UNAUTHENTICATED_USER": None,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "crawler": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
