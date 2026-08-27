from django.urls import re_path
from .consumer import ChatbotConsumer

websocket_urlpatterns = [
    # URL: ws://localhost:8000/ws/notifications/
    re_path(r'ws/v1/chatbot/$', ChatbotConsumer.as_asgi()),
]