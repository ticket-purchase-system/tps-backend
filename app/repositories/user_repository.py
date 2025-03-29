from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from app.models import AppUser

class UserRepository:
    @staticmethod
    def get_all():
        """Get all active users"""
        return AppUser.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID or return None"""
        try:
            return AppUser.objects.get(id=user_id, is_active=True)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_by_email(email):
        """Get user by email (case-insensitive)"""
        try:
            return AppUser.objects.get(user__email__iexact=email, is_active=True)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def create(user_data):
        """Create a new user"""
        user = User.objects.create_user(
            username=user_data['username'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            password=user_data['password'],
            email=user_data.get('email', '')
        )
        app_user = AppUser.objects.create(
            user=user,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            description=user_data.get('description', '')
        )
        return app_user

    @staticmethod
    def update(user, user_data):
        """Update existing user"""
        for field in ['first_name', 'last_name', 'description']:
            if field in user_data:
                setattr(user, field, user_data[field])

        if 'password' in user_data:
            user.set_password(user_data['password'])

        user.save()
        return user

    @staticmethod
    def delete(user):
        """Soft delete user (mark as inactive)"""
        user.is_active = False
        user.save()
        return user

    @staticmethod
    def search_users(query):
        """Search users by name or email"""
        return AppUser.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(user__email__icontains=query),
            is_active=True
        )