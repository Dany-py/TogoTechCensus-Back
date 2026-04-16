"""
ASGI config for Census project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

# IMPORTANT: Définir DJANGO_SETTINGS_MODULE AVANT tous les imports Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
from notification.middleware import CookieAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack # Importez ceci
from channels.routing import ProtocolTypeRouter, URLRouter
import notification.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack(
        AuthMiddlewareStack(
                URLRouter(
                    notification.routing.websocket_urlpatterns
                )
            )
        )
    })