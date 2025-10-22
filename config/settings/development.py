"""
Development settings
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Django Debug Toolbar (commented out - install if needed)
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
#     INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - allow all in development
CORS_ALLOW_ALL_ORIGINS = True
