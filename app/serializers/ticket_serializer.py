from rest_framework import serializers
from app.models.ticket import Ticket
from app.models.event import Event

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id']  # tylko ID na potrzeby ordera
