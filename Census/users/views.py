from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Users
from .serializers import UserSerializer
from rest_framework import viewsets, permissions, status



# View for the Users model
class UserView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        user = get_object_or_404(Users, id=pk)
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def patch(self, request, pk):
        user = get_object_or_404(Users, id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    permission_classes = [permissions.IsAuthenticated]         
    def get(self, request, pk=None):

        if pk:
            user = get_object_or_404(Users, id=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        user = request.user
        if user.is_authenticated:
            user_data = get_object_or_404(Users, id=user.pk)
            serializer = UserSerializer(user_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"Detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
