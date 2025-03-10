"""
ASGI config for naan_mudhalvan_monolith project.
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Set the Django settings module explicitly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "naan_mudhalvan_monolith.settings")
django.setup()  # Add this line to ensure Django is fully configured

# Import routing after Django is configured
import recruiters.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            recruiters.routing.websocket_urlpatterns
        )
    ),
})