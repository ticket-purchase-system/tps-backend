from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Event

class EventSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Event
        fields = ['id', 'title', 'date', 'price', 'description', 'created_by', 'created_at']
        read_only_fields = ['created_at']
