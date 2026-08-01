from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.conf import settings
from django.contrib.auth import get_user_model
from http.cookies import SimpleCookie


@database_sync_to_async
def get_user(user_id):
    """Get user by ID"""
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

@database_sync_to_async
def get_user_from_session(session_key):
    """Get user by Django's session key"""
    User = get_user_model()
    try:
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        if user_id:
            try:
                return User.objects.get(id=int(user_id))
            except User.DoesNotExist:
                return AnonymousUser()
    except (Session.DoesNotExist, KeyError, ValueError):
        pass
    return AnonymousUser()

class CookieAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        user = AnonymousUser()
        
        # Extraire l'utilisateur depuis les cookies de session Django
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"").decode()
        
        if cookie_header:
            cookies = SimpleCookie()
            print('Cookie :', cookies)
            cookies.load(cookie_header)
            
            # Récupérer le cookie de session Django
            session_cookie_name = settings.SESSION_COOKIE_NAME
            if session_cookie_name in cookies:
                session_key = cookies[session_cookie_name].value
                user = await get_user_from_session(session_key)
        
        # Ajouter l'utilisateur au "scope" (le contexte de la socket)
        scope["user"] = user
        return await self.inner(scope, receive, send)