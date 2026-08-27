
from rest_framework.pagination import PageNumberPagination
from .serializers import NotificationSerializer
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from crum import get_current_user
from .models import Notification


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class NotificationView(APIView):
    
    permissions.IsAuthenticated()
    def get(self, request):
        try:
            user = get_current_user()
            user_notification = Notification.objects.filter(recipient=user)
            #print("Notification de l'utilisateur :", user_notification)
            paginator = NotificationPagination()
            page = paginator.paginate_queryset(user_notification, request)
        
            if page is not None:
                serializer = NotificationSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        
            serializer = NotificationSerializer(user_notification, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"\n❌ Error {e}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    