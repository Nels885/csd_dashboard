import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from sbadmin.ws_urls import ws_urlpatterns

django_asgi_app = get_asgi_application()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sbadmin.settings.production")

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    "http": django_asgi_app,
    'websocket': URLRouter(ws_urlpatterns)
})
