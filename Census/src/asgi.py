"""
ASGI config for Census project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
import sys

# IMPORTANT: Définir DJANGO_SETTINGS_MODULE AVANT tous les imports Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

from whitenoise import WhiteNoise


from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
application = WhiteNoise(django_asgi_app, root='staticfiles/')

# --- Vérification Redis au démarrage ---
import redis as _redis
from django.conf import settings as _settings

def _check_redis():
    layer_config = _settings.CHANNEL_LAYERS['default']['CONFIG']
    hosts = layer_config.get('hosts', [])
    host = hosts[0] if hosts else None
    try:
        if isinstance(host, str):
            # URL complète (rediss://... ou redis://...)
            client = _redis.from_url(host, socket_connect_timeout=3)
        elif isinstance(host, dict):
            client = _redis.Redis(
                host=host['host'], port=host['port'],
                password=host.get('password'), ssl=host.get('ssl', False),
                socket_connect_timeout=3,
            )
        else:
            h, p = host if host else ('127.0.0.1', 6379)
            client = _redis.Redis(host=h, port=p, socket_connect_timeout=3)
        client.ping()
        print("[channels] ✅ Redis connecté avec succès.")
    except Exception as exc:
        print(f"[channels] ❌ Impossible de joindre Redis : {exc}", file=sys.stderr)
        sys.exit(1)

_check_redis()
# ---------------------------------------

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
import notification.routing
import chatbot.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(
                notification.routing.websocket_urlpatterns + chatbot.routing.websocket_urlpatterns
            )
        )
    ),
})