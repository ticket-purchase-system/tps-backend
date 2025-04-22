# app/serializers/user_serializer.py

from django.contrib.auth.models import User
from rest_framework import serializers
from app.models import AppUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},  # 👈 add this
            'email': {'required': False}
        }

class AppUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = AppUser
        fields = ['id', 'user', 'first_name', 'last_name', 'role', 'is_active']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        app_user = AppUser.objects.create(user=user, **validated_data)
        return app_user

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        if user_data:
            user = instance.user
            user.username = user_data.get('username', user.username)
            user.email = user_data.get('email', user.email)
            if 'password' in user_data and user_data['password']:
                user.set_password(user_data['password'])
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


