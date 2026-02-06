"""
WSGI config for Tapai Ko Sathi project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tapai_ko_sathi.settings")

application = get_wsgi_application()

