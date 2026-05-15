import os
from pathlib import Path
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def csv_env(name, default=""):
    return [item.strip() for item in config(name, default=default, cast=Csv()) if item.strip()]


def vercel_hosts():
    hosts = []
    for name in ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
        value = os.environ.get(name, "").strip()
        if value:
            hosts.append(value.removeprefix("https://").removeprefix("http://").rstrip("/"))
    return hosts


def is_vercel_runtime():
    return bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_URL"))


def database_config():
    default_sqlite = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    vercel_fallback_sqlite = "sqlite:////tmp/codetrack-unconfigured.sqlite3"
    primary = config("DATABASE_URL", default="")
    fallbacks = [
        config("POSTGRES_URL", default=""),
        config("POSTGRES_PRISMA_URL", default=""),
        config("POSTGRES_URL_NON_POOLING", default=""),
        config("DATABASE_URL_UNPOOLED", default=""),
    ]
    sqlite_url = primary.startswith("sqlite:")
    local_placeholder = "localhost" in primary or "127.0.0.1" in primary or "user:pass@" in primary
    invalid_vercel_database = is_vercel_runtime() and (sqlite_url or local_placeholder)
    if primary and not invalid_vercel_database:
        return primary, True
    for candidate in fallbacks:
        if candidate:
            return candidate, True
    if is_vercel_runtime():
        return vercel_fallback_sqlite, False
    return primary or default_sqlite, True


SECRET_KEY = config("SECRET_KEY", default="change-me-in-production")
DEBUG = config("DEBUG", default=False, cast=env_bool)
if is_vercel_runtime() and "DEBUG" not in os.environ:
    DEBUG = False
ALLOWED_HOSTS = sorted(set(csv_env("ALLOWED_HOSTS", "localhost,127.0.0.1") + vercel_hosts()))
CSRF_TRUSTED_ORIGINS = sorted(
    set(
        csv_env("CSRF_TRUSTED_ORIGINS")
        + [f"https://{host}" for host in ALLOWED_HOSTS if host.endswith(".vercel.app")]
    )
)
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
OPENAI_MODEL = config("OPENAI_MODEL", default="gpt-4.1-mini")
AI_GRADING_ENABLED = config("AI_GRADING_ENABLED", default=bool(OPENAI_API_KEY), cast=env_bool)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_htmx',
    'accounts',
    'problems',
    'quizzes',
    'progress',
    'announcements',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'codetrack.middleware.RequireConfiguredDatabaseMiddleware',
]

ROOT_URLCONF = 'codetrack.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'codetrack.wsgi.application'

DATABASE_URL, DATABASE_CONFIGURED = database_config()
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=config("DB_CONN_MAX_AGE", default=0 if is_vercel_runtime() else 600, cast=int),
        ssl_require=config("DB_SSL_REQUIRE", default=False, cast=env_bool),
    )
}
if "pooler." in DATABASE_URL or "-pooler." in DATABASE_URL:
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
DATABASES["default"]["CONN_HEALTH_CHECKS"] = config("DB_CONN_HEALTH_CHECKS", default=True, cast=env_bool)

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = config("TIME_ZONE", default="Asia/Manila")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

AUTH_PROFILE_MODULE = 'accounts.Profile'

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = config("USE_X_FORWARDED_HOST", default=is_vercel_runtime(), cast=env_bool)

if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=env_bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": config("LOG_LEVEL", default="INFO")},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
