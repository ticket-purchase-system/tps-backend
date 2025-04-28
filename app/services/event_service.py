from django.utils import timezone
from app.repositories.event_repository import EventRepository

class EventService:
    def __init__(self):
        self.event_repository = EventRepository()

    def create_event(self, title, type, date, price, description, created_by, start_hour=None,
                     end_hour=None, place=None, seats_no=None, artists=None):
        """Create a new event"""
        event = self.event_repository.create(
            title=title,
            type=type,
            date=date,
            start_hour=start_hour,
            end_hour=end_hour,
            place=place,
            price=price,
            seats_no=seats_no,
            description=description,
            created_by=created_by,
            created_at=timezone.now()
        )

        if artists:
            self.event_repository.add_artists_to_event(event, artists)

        return event

    def update_event(self, event_id, title=None, type=None, date=None, price=None,
                     description=None, start_hour=None, end_hour=None, place=None,
                     seats_no=None, artists=None):
        """Update an existing event"""
        event = self.event_repository.get_by_id(event_id)
        if not event:
            return None

        update_data = {
            'title': title,
            'type': type,
            'date': date,
            'price': price,
            'description': description,
            'start_hour': start_hour,
            'end_hour': end_hour,
            'place': place,
            'seats_no': seats_no,
            'artists': artists
        }

        update_data = {k: v for k, v in update_data.items() if v is not None}

        updated_event = self.event_repository.update(event, **update_data)

        if artists:
            self.event_repository.add_artists_to_event(updated_event, artists)

        return updated_event

    def get_event(self, event_id):
        """Get an event by ID with its details"""
        return self.event_repository.get_event_with_details(event_id)

    def get_events(self, query=None, start_date=None, end_date=None):
        """Get filtered events with their details"""
        return self.event_repository.get_events_with_details(query, start_date, end_date)