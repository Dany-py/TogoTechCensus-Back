from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
"""
router.register(r'authors', AuthorViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'categories', CategorieViewSet)
router.register(r'technologies', TechnologieViewSet)"""

app_name = 'projects'

urlpatterns = [
    path('', ProjectView.as_view(), name='projects-list'),
    path('categories/', CategorieView.as_view(), name='categories-list'),
    path('technologies/', TechnologieView.as_view(), name='technologies-list'),
    path('authors/', AuthorView.as_view(), name='authors-list'),
]