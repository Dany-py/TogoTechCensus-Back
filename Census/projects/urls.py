from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UnAuthenticateProjectView, ProjectView, ProjectStats, CategoriesView, TechnologiesView, AuthorView

router = DefaultRouter()

app_name = 'projects'

urlpatterns = [
    path('', ProjectView.as_view(), name='projects-list'),
    path('unauth/', UnAuthenticateProjectView.as_view(), name='projects-unauthenticate'),
    path('<int:id>/', ProjectView.as_view(), name='projects-detail'),
    path('stats/', ProjectStats.as_view(), name='projects-stats'),
    path('stats/<int:id>/', ProjectStats.as_view(), name='projects-stats-specify'),
    path('author/', AuthorView.as_view(), name='project-author'),
    path('categories/', CategoriesView.as_view(), name='project-categories'),
    path('technologies/', TechnologiesView.as_view(), name='project-technologies')
]