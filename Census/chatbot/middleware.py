import uuid
from urllib.parse import parse_qs
from crum import get_current_user
from http.cookies import SimpleCookie
from django.utils.deprecation import MiddlewareMixin

class AnonymousIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        anonymous_id = request.COOKIES.get('anonymous_id')
        if not anonymous_id:
            anonymous_id = str(uuid.uuid4())
            request.anonymous_id = anonymous_id
            request._new_anonymous_id = True  # flag pour savoir qu'il faut set le cookie
        else:
            request.anonymous_id = anonymous_id
            request._new_anonymous_id = False

    def process_response(self, request, response):
        if getattr(request, '_new_anonymous_id', False):
            response.set_cookie(
                'anonymous_id',
                request.anonymous_id,
                max_age=60 * 60 * 24 * 365,  # 1 an
                httponly=True,
                samesite='Lax'
            )
        return response
    

class ASGIAnonymousIDMiddleware:
    
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        if scope["type"] == "websocket":
            new_uuid = str(uuid.uuid4())
            scope["chat_uuid"] = new_uuid