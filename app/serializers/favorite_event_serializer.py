from rest_framework import serializers
from app.models.user_event_favorite import UserEventFavorite

class UserEventFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEventFavorite
        fields = ['user', 'event', 'is_favorite']
