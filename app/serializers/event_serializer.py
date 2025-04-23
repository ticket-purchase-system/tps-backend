from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Event
from app.serializers.artist_serializer import ArtistSerializer


class EventSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    artists = ArtistSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'type', 'date', 'start_hour', 'end_hour',
                  'place', 'price', 'seats_no', 'description', 'created_by',
                  'created_at', 'artists']
        read_only_fields = ['created_at']