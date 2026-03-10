from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Users
from .serializers import UserSerializer


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
                
    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(Users, id=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)