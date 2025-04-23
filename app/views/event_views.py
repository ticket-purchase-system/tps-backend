from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from urllib3 import request

from app.serializers.event_serializer import EventSerializer
from app.services.event_service import EventService
from app.models.event import Event
from app.models.artist import Artist
from app.models.user import AppUser


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    event_service = EventService()

    @action(detail=False, methods=['post'])
    def create_event(self, request):
        """Custom endpoint to create an event."""
        title = request.data.get('title')
        type = request.data.get('type', 'CONCERT')  # Default type
        date = request.data.get('date')
        price = request.data.get('price')
        description = request.data.get('description')
        user_id = request.data.get('created_by')

        # New fields
        start_hour = request.data.get('start_hour')
        end_hour = request.data.get('end_hour')
        place = request.data.get('place')
        seats_no = request.data.get('seats_no')
        artist_ids = request.data.get('artists', [])

        artists = []
        if artist_ids:
            artists = Artist.objects.filter(id__in=artist_ids)

        print(request.data)
        try:
            created_by = AppUser.objects.get(id=user_id)
            event = self.event_service.create_event(
                title, type, date, price, description, created_by.user,
                start_hour, end_hour, place, seats_no, artists
            )
            serializer = self.get_serializer(event)
            return Response(serializer.data, status=201)
        except AppUser.DoesNotExist:
            print("User not found!")
            return Response({'error': 'User not found'}, status=400)

        except Exception as e:
            print("Unexpected error:", e)
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['put'])
    def update_event(self, request, pk=None):
        """Custom endpoint to update an event."""
        title = request.data.get('title')
        type = request.data.get('type')
        date = request.data.get('date')
        price = request.data.get('price')
        description = request.data.get('description')

        # New fields
        start_hour = request.data.get('start_hour')
        end_hour = request.data.get('end_hour')
        place = request.data.get('place')
        seats_no = request.data.get('seats_no')
        artist_ids = request.data.get('artists')

        artists = None
        if artist_ids:
            artists = Artist.objects.filter(id__in=artist_ids)

        event = self.event_service.update_event(
            pk, title, type, date, price, description,
            start_hour, end_hour, place, seats_no, artists
        )

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

        event_data = self.event_service.get_events(query, start_date, end_date)

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
        event_data = self.event_service.get_event(pk)

        if event_data:
            event_serializer = EventSerializer(event_data['event'])
            event_details = event_data['details']

            return Response({
                'event': event_serializer.data,
                'details': {
                    'location': event_details.location if event_details else None,
                    'rules': event_details.rules if event_details else None,
                    'max_attendees': event_details.max_attendees if event_details else None,
                    'additional_info': event_details.additional_info if event_details else None
                }
            })
        return Response({"detail": "Event not found"}, status=404)