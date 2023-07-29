import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from .routing import websocket_urlpatterns
from .middleware import TokenAuthMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket":
            TokenAuthMiddleware(
                URLRouter(
                    websocket_urlpatterns
                    )

        )
    }
)
