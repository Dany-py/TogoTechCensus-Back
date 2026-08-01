from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()

app_name = 'notifications'

urlpatterns = [
    path('', NotificationView.as_view(), name='notifications-list'),
]