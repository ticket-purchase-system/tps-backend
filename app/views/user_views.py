from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from app.serializers.user_serializer import UserSerializer
from app.services.user_service import UserService

class UserViewSet(viewsets.ViewSet):
    """
    A viewset for managing users with business logic encapsulated in UserService.
    """

    def list(self, request):
        """Search users with a query"""
        query = request.query_params.get('query', '')
        users = UserService.search_users(query)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new user"""
        user_data = request.data
        try:
            user = UserService.create_user(user_data)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Update an existing user"""
        updated_data = request.data
        try:
            user = UserService.update_user(pk, updated_data)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Retrieve a user by ID"""
        try:
            user = User.objects.get(id=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """Delete a user"""
        try:
            user = User.objects.get(id=pk)
            user.is_active = False
            user.save()
            return Response({"detail": "User deleted"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)