
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'message': 'csrfToken set.'})

def home(request):
    return JsonResponse({'message': 'Welcome to TogoTechCensus!'})