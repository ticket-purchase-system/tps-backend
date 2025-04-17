from rest_framework import serializers
from app.models.event_details import EventDetails

class EventDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDetails
        fields = ['venue', 'rules', 'start_date', 'end_date', 'description']
