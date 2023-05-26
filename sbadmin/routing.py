import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sbadmin.settings.production")

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    "http": django_asgi_app,
})
