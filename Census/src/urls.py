"""
URL configuration for Census project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import get_csrf_token
#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/csrf/', get_csrf_token, name='get_csrf_token'),
    path('api/v1/auth/', include('social_django.urls', namespace='social')),
    path('api/v1/users/', include('users.urls', namespace='user')),
    path('api/v1/projects/', include('projects.urls', namespace='project')),
    path('api/v1/notification/', include('notification.urls', namespace='notification'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
