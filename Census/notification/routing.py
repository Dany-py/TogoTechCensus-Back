from django.urls import re_path
from .consumer import NotificationConsumer

websocket_urlpatterns = [
    # URL: ws://localhost:8000/ws/notifications/
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]