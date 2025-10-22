"""
Django settings package
Import settings based on DJANGO_SETTINGS_MODULE environment variable
"""
import os

# Default to development settings
ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .development import *
