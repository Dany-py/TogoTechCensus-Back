import logging

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Users
from .serializers import UserSerializer

logger = logging.getLogger(__name__)


# View for the Users model
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        logger.debug(
            "UserView.get called | path=%s | authenticated=%s | user=%s",
            request.path,
            request.user.is_authenticated,
            getattr(request.user, "pk", None),
        )

        # Guard: should already be blocked by permission_classes, but return an
        # explicit 401 (not 403) so the frontend can distinguish "not logged in"
        # from "logged in but forbidden".
        if not request.user.is_authenticated:
            logger.warning(
                "Unauthenticated request to UserView.get | path=%s | session=%s",
                request.path,
                request.session.session_key,
            )
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if pk:
            logger.debug("Fetching user by pk=%s", pk)
            user = get_object_or_404(Users, id=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Fetch the profile for the currently authenticated user.
        try:
            user_data = Users.objects.get(id=request.user.pk)
        except Users.DoesNotExist:
            logger.error(
                "Authenticated user pk=%s has no matching Users profile",
                request.user.pk,
            )
            return Response(
                {"detail": "User profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        logger.debug("Returning profile for user pk=%s", request.user.pk)
        serializer = UserSerializer(user_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
