from __future__ import absolute_import
import celery.schedules
from pathlib import Path

from ..celery import app as celery_app

# Basic Settings
BASE_DIR = Path(__file__).resolve().parent.parent


# Applications
INSTALLED_APPS = [
    "multicast.apps.add",
    "multicast.apps.manage",
    "multicast.apps.view",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "multicast.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "multicast.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Login settings
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "serve"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Defaults
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Celery settings
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_BEAT_SCHEDULE = {
    "scrape_for_streams": {
        "task": "multicast.apps.add.tasks.scrape_for_streams",
        "schedule": celery.schedules.crontab(minute=0, hour=0),
        "args": (),
    },
    "clean_inactive_streams": {
        "task": "multicast.apps.add.tasks.clean_inactive_streams",
        "schedule": celery.schedules.crontab(minute=0, hour=1),
        "args": (),
    },
}


# Trending streams constants
TRENDING_STREAM_USAGE_WEIGHT = 0.9
TRENDING_STREAM_INIT_SCORE = 1.0
TRENDING_STREAM_MAX_SIZE = 20
TRENDING_STREAM_MAX_VISIBLE_SIZE = 10


# Import secret.py
try:
    from .secret import *
except ImportError:
    pass
