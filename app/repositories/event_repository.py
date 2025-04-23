from django.db.models import Q
from app.models.event import Event
from app.models.event_details import EventDetails
from app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository):
    model = Event

    def get_event_with_details(self, event_id):
        """Get an event and its details by ID"""
        event = self.get_by_id(event_id)
        if not event:
            return None

        try:
            details = EventDetails.objects.get(event=event)
        except EventDetails.DoesNotExist:
            details = None

        return {
            'event': event,
            'details': details
        }

    def get_filtered_events(self, query=None, start_date=None, end_date=None):
        """Get events with optional filtering"""
        filters = Q()

        if query:
            filters &= (Q(title__icontains=query) | Q(description__icontains=query))

        if start_date:
            filters &= Q(date__gte=start_date)

        if end_date:
            filters &= Q(date__lte=end_date)

        return self.model.objects.filter(filters).order_by('date')

    def get_events_with_details(self, query=None, start_date=None, end_date=None):
        """Get filtered events with their details"""
        events = self.get_filtered_events(query, start_date, end_date)

        result = []
        for event in events:
            try:
                details = EventDetails.objects.get(event=event)
            except EventDetails.DoesNotExist:
                details = None

            result.append({
                'event': event,
                'details': details
            })

        return result

    def add_artists_to_event(self, event, artists):
        """Add artists to an event"""
        if artists:
            event.artists.set(artists)
        return event