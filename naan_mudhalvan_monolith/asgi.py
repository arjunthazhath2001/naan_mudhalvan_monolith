"""
ASGI config for naan_mudhalvan_monolith project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import recruiters.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "naan_mudhalvan_monolith.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            recruiters.routing.websocket_urlpatterns
        )
    ),
})