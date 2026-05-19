"""
WSGI config for lms project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_core.settings')

application = get_wsgi_application()
