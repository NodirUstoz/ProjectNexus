"""
Development-specific Django settings for ProjectNexus.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# Additional development apps
INSTALLED_APPS += []  # noqa: F405

# CORS - allow all in development
CORS_ALLOW_ALL_ORIGINS = True

# Use console email backend in development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable throttling in development
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}  # noqa: F405

# Simplified static file serving for development
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Debug logging
LOGGING["loggers"]["django.db.backends"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "WARNING",
    "propagate": False,
}
