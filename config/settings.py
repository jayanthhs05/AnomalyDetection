from decouple import config
from pathlib import Path

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-k&(+f6t_k7bf_alsfrfphy&@%z_+urj16wdav%c)3)zm)()g3^"


DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "detection",
    "django_celery_beat",
    "accounts",
    "crispy_forms",
    "crispy_bootstrap5",
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

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": config("MYSQL_ENGINE"),
        "NAME": config("MYSQL_DATABASE"),
        "USER": config("MYSQL_USER"),
        "PASSWORD": config("MYSQL_PASSWORD"),
        "HOST": config("MYSQL_HOST"),
        "PORT": config("MYSQL_PORT", cast=int),
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_ALL_TABLES'"},
    }
}


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


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/1"
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "score-every-5-min": {
        "task": "detection.tasks.score_new_data",
        "schedule": 300,
    }
}

CELERY_TIMEZONE = "Asia/Kolkata"
CELERY_ENABLE_UTC = False

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK         = "bootstrap5"

LOGIN_REDIRECT_URL  = "home"
LOGOUT_REDIRECT_URL = "home"