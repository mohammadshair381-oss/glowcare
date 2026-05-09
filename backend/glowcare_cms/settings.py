from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
  DEBUG=(bool, False),
  SECRET_KEY=(str, "dev-only-change-me"),
  ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
  DB_ENGINE=(str, "django.db.backends.postgresql"),
  DB_NAME=(str, "glowcare"),
  DB_USER=(str, "glowcare"),
  DB_PASSWORD=(str, "glowcare"),
  DB_HOST=(str, "127.0.0.1"),
  DB_PORT=(str, "5432"),
  MEDIA_URL=(str, "/media/"),
)

environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
  "django.contrib.admin",
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.messages",
  "django.contrib.staticfiles",
  "django.contrib.humanize",

  "rest_framework",
  "django_filters",
  "django_htmx",

  "apps.catalog.apps.CatalogConfig",
  "apps.cms.apps.CmsConfig",
  "apps.dashboard.apps.DashboardConfig",
  "apps.api.apps.ApiConfig",
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
  "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "glowcare_cms.urls"

TEMPLATES = [
  {
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [str(BASE_DIR / "templates")],
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

WSGI_APPLICATION = "glowcare_cms.wsgi.application"

DATABASES = {
  "default": {
    "ENGINE": env("DB_ENGINE"),
    "NAME": env("DB_NAME"),
    "USER": env("DB_USER"),
    "PASSWORD": env("DB_PASSWORD"),
    "HOST": env("DB_HOST"),
    "PORT": env("DB_PORT"),
  }
}

if DATABASES["default"]["ENGINE"].endswith("sqlite3"):
  DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": str(BASE_DIR / "db.sqlite3"),
  }

AUTH_PASSWORD_VALIDATORS = [
  {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
  {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
  {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
  {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATICFILES_DIRS = [
  str(BASE_DIR.parent),  # serves existing premium frontend assets (css/, js/, assets/, style.css, script.js)
  str(BASE_DIR / "static"),
]
STORAGES = {
  "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
  # Avoid hashed filenames because the frontend fetches component fragments by fixed paths.
  "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

MEDIA_URL = env("MEDIA_URL")
MEDIA_ROOT = str(BASE_DIR.parent / "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "dashboard:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "dashboard:login"

REST_FRAMEWORK = {
  "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend", "rest_framework.filters.OrderingFilter"],
  "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
  "PAGE_SIZE": 24,
}

# ye to mene khud kiya he
X_FRAME_OPTIONS = "SAMEORIGIN"