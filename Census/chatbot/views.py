from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework import permissions, status
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from .permissions import IsOwnerOrReadOnly
from .models import Conversation, Message

class ProjectPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class MessageView(APIView):

    def get_permissions(self):
        try:
            if self.request.method == 'POST':
                return [permissions.AllowAny()]
        
            if self.request.method in ['GET', 'PATCH', 'DELETE']:
                return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        
            return []
        except Exception as e:
            print(f"\n❌ Erreur dans get_permissions : {e}")
            return []
    
    def post(self, request):

        try:
            with transaction.atomic():
                conversation_data = request.data.get('conversation')
                message_serializer = MessageSerializer(data=request.data)

                if not message_serializer.is_valid():
                    return Response(message_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                conversation_serializer = ConversationSerializer(data=conversation_data)
                if not conversation_serializer.is_valid():
                    return Response(conversation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                if request.user.is_authenticated:
                    user = request.user.pk
                    conversation = conversation_serializer.save(user=user)
                    message_serializer.save(conversation=conversation)
                    return Response(message_serializer.data, status=status.HTTP_201_CREATED)
                    
                else:
                    anonymous_id = request.anonymous_id
                    conversation = conversation_serializer.save(anonymous_id=anonymous_id)
                    message_serializer.save(conversation=conversation)
                    return Response(message_serializer.data, status=status.HTTP_201_CREATED)
                  
        except Exception as e:
            print(f"\n❌ Post View Error : {e}")
            return Response({"detail": "Une erreur est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    def get(self, request):
        try:
            user_message = Message.objects.filter(user=request.user, is_deleted=False).order_by('created_at')
            if request.query_params:
                message = Message.objects.filter(id=request.query_params.get('id'), is_deleted=False)
                serializer = MessageSerializer(message, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
            paginator = ProjectPagination()
            page = paginator.paginate_queryset(user_message, request)
        
            if page is not None:
                serializer = MessageSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        
            serializer = MessageSerializer(user_message, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"\n❌ Post View Error : {e}")
            return Response({"detail": "Une erreur est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def patch(self, request):

        try:
            instance = Message.objects.get(pk=request.query_params.get('id'))
            serializer = MessageSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Une erreur est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        try:
            instance = Message.objects.get(pk=request.query_params.get('id'))
            delete_data = {
                'is_deleted': True
            }
            serializer = MessageSerializer(instance, delete_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Une erreur est survenue."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#class Conversation(APIView):