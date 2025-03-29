from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from app.repositories.user_repository import UserRepository

class UserService:
    @staticmethod
    def create_user(user_data):
        """Create a new user with business logic"""
        if 'username' not in user_data:
            raise ValidationError("Username is required")

        if User.objects.filter(username=user_data['username']).exists():
            raise ValidationError("Username already exists")

        user = UserRepository.create(user_data)

        return user

    @staticmethod
    def update_user(user_id, updated_data):
        """Update existing user with business logic"""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")

        updated_user = UserRepository.update(user, updated_data)

        return updated_user

    @staticmethod
    def search_users(query):
        """Search users with complex business logic if needed"""
        users = UserRepository.search_users(query)
        return users