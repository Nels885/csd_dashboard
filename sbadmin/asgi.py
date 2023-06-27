"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sbadmin.settings.production")

application = get_asgi_application()
