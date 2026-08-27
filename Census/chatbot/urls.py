from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MessageView

router = DefaultRouter()

app_name = 'chatbot'

urlpatterns = [
    path('', MessageView.as_view(), name='message-list'),
    path('<int:id>/', MessageView.as_view(), name='message-specify'),
]