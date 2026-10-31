import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# Load simple KEY=value pairs from .env without an additional dependency.
env_file = BASE_DIR / ".env"
if env_file.exists():
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-before-deployment")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "core",
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
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "core" / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages", "core.context_processors.site_choices",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.environ.get("DATABASE_NAME") or str(BASE_DIR / "db.sqlite3"),
}}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# ---------------------------------------------------------------------------
# NUVAIX enquiry delivery (WhatsApp group relay + email) and Android app links
# All values come from environment variables / .env. See README.md.
# ---------------------------------------------------------------------------
def _env(name, default=""):
    return os.environ.get(name, default).strip()

# Public WhatsApp number used for the floating "Chat with us" button and as the
# manual fallback ("Open WhatsApp") when the group relay is not configured.
WHATSAPP_NUMBER = "".join(ch for ch in _env("WHATSAPP_NUMBER", "2349132165565") if ch.isdigit())
WHATSAPP_DISPLAY = _env("WHATSAPP_DISPLAY", "+234 913 216 5565")

# Staff-only reference: the invite link of the internal NUVAIX WhatsApp group.
# It is only shown publicly when WHATSAPP_GROUP_PUBLIC=1 (anyone with it can join the group).
WHATSAPP_GROUP_INVITE_URL = _env("WHATSAPP_GROUP_INVITE_URL")
# Free mode: when 1, customers who are not relayed automatically are sent to the group
# invite link above (their message is copied so they can paste it into the group).
# They join the group and their message is visible to its other members.
WHATSAPP_GROUP_PUBLIC = _env("WHATSAPP_GROUP_PUBLIC", "0") == "1"

# Group relay through a WhatsApp gateway API (Whapi.cloud-style JSON API).
# Leave the token / group id empty to disable the relay.
WHATSAPP_GATEWAY_URL = _env("WHATSAPP_GATEWAY_URL", "https://gate.whapi.cloud/messages/text")
WHATSAPP_GATEWAY_TOKEN = _env("WHATSAPP_GATEWAY_TOKEN")
WHATSAPP_GROUP_ID = _env("WHATSAPP_GROUP_ID")  # e.g. 120363012345678901@g.us

# Email delivery. The enquiry is sent to NUVAIX_EMAIL with Reply-To = the customer.
NUVAIX_EMAIL = _env("NUVAIX_EMAIL")
EMAIL_HOST = _env("EMAIL_HOST")
EMAIL_PORT = int(_env("EMAIL_PORT", "587") or 587)
EMAIL_HOST_USER = _env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = _env("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = _env("EMAIL_USE_SSL", "0") == "1"
EMAIL_USE_TLS = (_env("EMAIL_USE_TLS", "1") == "1") and not EMAIL_USE_SSL
DEFAULT_FROM_EMAIL = _env("DEFAULT_FROM_EMAIL") or EMAIL_HOST_USER or "no-reply@localhost"
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend" if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)
# With no SMTP host, emails are only printed to the terminal, which is fine while
# developing (DEBUG=1) but is NOT a real delivery in production.
EMAIL_CONFIGURED = bool(EMAIL_HOST) or DEBUG

# Android app (Google Play). One default link, optional per-division overrides:
#   PLAY_STORE_URL_PAINT, PLAY_STORE_URL_TECHNOLOGY, PLAY_STORE_URL_HEALTHCARE,
#   PLAY_STORE_URL_REAL_ESTATE, ... (slug upper-cased, "-" -> "_")
ANDROID_APP_PACKAGE = _env("ANDROID_APP_PACKAGE")  # e.g. com.nuvaix.app
PLAY_STORE_URL = _env("PLAY_STORE_URL") or (
    f"https://play.google.com/store/apps/details?id={ANDROID_APP_PACKAGE}" if ANDROID_APP_PACKAGE else ""
)
PLAY_STORE_URLS = {
    key[len("PLAY_STORE_URL_"):]: value.strip()
    for key, value in os.environ.items()
    if key.startswith("PLAY_STORE_URL_") and value.strip()
}

# Simple anti-spam for the public enquiry form (submissions per IP per hour).
ENQUIRY_RATE_LIMIT = int(_env("ENQUIRY_RATE_LIMIT", "8") or 8)

# `manage.py test` has no collectstatic manifest, so use plain static storage there.
if "test" in sys.argv:
    STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
