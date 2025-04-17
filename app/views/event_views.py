from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from app.serializers.event_serializer import EventSerializer
from app.services.event_service import create_event, update_event, get_event, get_events
from django.contrib.auth.models import User
from app.models.event import Event

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=False, methods=['post'])
    def create_event(self, request):
        """
        Custom endpoint to create an event.
        """
        title = request.data.get('title')
        date = request.data.get('date')
        price = request.data.get('price')
        description = request.data.get('description')
        user_id = request.data.get('created_by')

        try:
            created_by = User.objects.get(id=user_id)
            event = create_event(title, date, price, description, created_by)
            serializer = self.get_serializer(event)
            return Response(serializer.data, status=201)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)

    @action(detail=True, methods=['put'])
    def update_event(self, request, pk=None):
        """
        Custom endpoint to update an event.
        """
        title = request.data.get('title')
        date = request.data.get('date')
        price = request.data.get('price')
        description = request.data.get('description')

        event = update_event(pk, title, date, price, description)

        if event:
            serializer = self.get_serializer(event)
            return Response(serializer.data)
        else:
            return Response({'error': 'Event not found'}, status=404)

    def list(self, request, *args, **kwargs):
        """List all events, optionally filtered by query or date"""
        query = request.query_params.get('query', '')
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        event_data = get_events(query, start_date, end_date)

        events = [
            {
                'event': EventSerializer(event['event']).data,
                'details': {
                    'location': event['details'].location if event['details'] else None,
                    'rules': event['details'].rules if event['details'] else None,
                    'max_attendees': event['details'].max_attendees if event['details'] else None,
                    'additional_info': event['details'].additional_info if event['details'] else None
                }
            }
            for event in event_data
        ]

        return Response(events)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single event by ID with details"""
        pk = kwargs['pk']
        event_data = get_event(pk)
        if event_data:
            event_serializer = EventSerializer(event_data['event'])
            event_details = event_data['details']

            return Response({
                'event': event_serializer.data,
                'details': {
                    'location': event_details.location if event_details else None,
                    'ruleKs': event_details.rules if event_details else None,
                    'max_attendees': event_details.max_attendees if event_details else None,
                    'additional_info': event_details.additional_info if event_details else None
                }
            })
        return Response({"detail": "Event not found"}, status=404)