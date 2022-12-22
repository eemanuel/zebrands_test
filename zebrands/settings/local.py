from zebrands.settings.common import *

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = environ.get("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD", default=None)
