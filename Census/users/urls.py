from django.urls import path
from .views import UserView

app_name = 'users'

urlpatterns = [
    path('', UserView.as_view(), name='users-list'),
    path('me/', UserView.as_view(), name='user-detail'),
    #path('<int:pk>/', UserView.as_view(), name='users-detail'),
]