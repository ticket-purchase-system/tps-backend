from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from app.models import AppUser
from app.serializers.user_serializer import UserSerializer, AppUserSerializer
from app.services.user_service import UserService
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

class UserViewSet(viewsets.ViewSet):
    """
    A viewset for managing users with business logic encapsulated in UserService.
    """
    permission_classes = [AllowAny]

    def list(self, request):
        """Get all users"""
        users = AppUser.objects.filter(is_active=True)
        serializer = AppUserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new user (AppUser + User)"""
        serializer = AppUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(AppUserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Update user and nested user fields"""
        try:
            user = AppUser.objects.get(id=pk, is_active=True)
            serializer = AppUserSerializer(user, data=request.data, partial=False)
            if serializer.is_valid():
                updated_user = serializer.save()
                return Response(AppUserSerializer(updated_user).data)
            print("Serializer validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        """Retrieve a single user"""
        try:
            if str(pk).isdigit():
                user = AppUser.objects.get(id=pk, is_active=True)
            else:
                user = AppUser.objects.get(user__username=pk, is_active=True)

            serializer = AppUserSerializer(user)
            return Response(serializer.data)
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """Hard delete the user and related auth user"""
        try:
            app_user = AppUser.objects.get(id=pk)
            user = app_user.user  # related auth User
            app_user.delete()  # delete AppUser
            user.delete()  # delete Django's User as well (optional but typical)
            return Response({"detail": "User permanently deleted"}, status=status.HTTP_204_NO_CONTENT)
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='reset-password', url_name='reset_password')
    def reset_password(self, request):
        """Reset user password"""
        username = request.data.get('username')
        new_password = request.data.get('new_password')

        if not username or not new_password:
            return Response(
                {"detail": "Username and new password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password reset successfully"})
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
