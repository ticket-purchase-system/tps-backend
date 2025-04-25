from app.repositories.ticket_repository import TicketRepository

class TicketService:
    @staticmethod
    def add_to_basket(user, ticket_data):
        print("TICKET DATA:", ticket_data)
        return TicketRepository.create_ticket(user=user, **ticket_data)

    @staticmethod
    def get_user_basket(user):
        return TicketRepository.get_tickets_by_user(user)
