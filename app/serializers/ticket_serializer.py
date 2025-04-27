from rest_framework import serializers
from app.models.ticket import Ticket
from app.models.event import Event

class TicketSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    class Meta:
        model = Ticket
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
