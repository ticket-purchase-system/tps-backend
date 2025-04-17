from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from app.models.event import Event
from django.utils import timezone
from app.models.event_details import EventDetails

def create_event(title, date, price, description, created_by):
    """
    Create and save a new event.
    :param title: The title of the event
    :param date: The date of the event
    :param price: The price for attending the event
    :param description: A description of the event
    :param created_by: The user who created the event
    :return: The created Event object
    """
    event = Event(
        title=title,
        date=date,
        price=price,
        description=description,
        created_by=created_by,
        created_at=timezone.now()
    )
    event.save()
    return event


def update_event(event_id, title=None, date=None, price=None, description=None):
    """
    Update an existing event.
    :param event_id: The ID of the event to update
    :param title: The new title of the event (optional)
    :param date: The new date of the event (optional)
    :param price: The new price of the event (optional)
    :param description: The new description of the event (optional)
    :return: The updated Event object, or None if not found
    """
    try:
        event = Event.objects.get(id=event_id)

        if title:
            event.title = title
        if date:
            event.date = date
        if price:
            event.price = price
        if description:
            event.description = description

        event.save()
        return event
    except Event.DoesNotExist:
        return None

def get_event(event_id):
    """
    Retrieve an event and its details by event ID.
    :param event_id: The ID of the event to retrieve
    :return: A dictionary containing the Event and its details if found, None otherwise
    """
    try:
        event = Event.objects.get(id=event_id)
        event_details = EventDetails.objects.get(event=event)
        return {
            'event': event,
            'details': event_details
        }
    except ObjectDoesNotExist:
        return None


def get_events(query=None, start_date=None, end_date=None):
    """
    Retrieve a list of events, with optional filtering, along with event details.
    :param query: A search query to filter events by title or description
    :param start_date: A start date filter for the event date
    :param end_date: An end date filter for the event date
    :return: A list of dictionaries containing Event and EventDetails
    """
    filters = Q()

    if query:
        filters &= (Q(title__icontains=query) | Q(description__icontains=query))

    if start_date:
        filters &= Q(date__gte=start_date)

    if end_date:
        filters &= Q(date__lte=end_date)

    events = Event.objects.filter(filters).order_by('date')

    event_data = []
    for event in events:
        try:
            event_details = EventDetails.objects.get(event=event)
            event_data.append({
                'event': event,
                'details': event_details
            })
        except EventDetails.DoesNotExist:
            event_data.append({
                'event': event,
                'details': None
            })

    return event_data