from app.models.ticket import Ticket
from app.models.event import Event


class TicketRepository:
    @staticmethod
    def create_ticket(user, event, seat, quantity=1, is_group=False):
        # Konwertuj ID na obiekt Event
        if isinstance(event, Event):
            event_instance = event
        else:
            event_instance = Event.objects.get(pk=event)

        return Ticket.objects.create(
            user=user,
            event=event_instance,
            seat=seat,
            quantity=quantity,
            is_group=is_group
        )

    @staticmethod
    def get_tickets_by_user(user):
        return Ticket.objects.filter(user=user)
