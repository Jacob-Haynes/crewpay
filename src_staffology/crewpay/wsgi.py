"""
WSGI config for crewpay project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crewpay.settings")

application = get_wsgi_application()
apps.populate(settings.INSTALLED_APPS)
