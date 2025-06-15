import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsa_backend.settings')
django.setup()

import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from app.services.ticket_service import TicketService
from app.models.ticket import Ticket
from app.services.event_service import EventService

class TicketServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ticketuser', password='123')
        self.event_service = EventService()
        self.event = self.event_service.create_event(
            title='Ticket Event',
            type='Concert',
            date='2025-12-31',
            price=50.00,
            description='Ticket Event Desc',
            created_by=self.user,
            start_hour='19:00',
            end_hour='21:00',
            place='Big Hall',
            seats_no=100,
            artists=[]
        )

    def test_add_to_basket(self):
        ticket_data = {
            'event': self.event,
            'seat': 'A1',
            'quantity': 2,
            'is_group': False
        }

        ticket = TicketService.add_to_basket(user=self.user, ticket_data=ticket_data)
        self.assertIsNotNone(ticket.id)
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.event, self.event)
        self.assertEqual(ticket.quantity, 2)

    def test_get_user_basket(self):
        # Add multiple tickets
        for i in range(3):
            TicketService.add_to_basket(user=self.user, ticket_data={
                'event': self.event,
                'seat': f'B{i+1}',
                'quantity': 1,
                'is_group': False
            })

        basket = TicketService.get_user_basket(user=self.user)
        self.assertEqual(len(basket), 3)
        for ticket in basket:
            self.assertEqual(ticket.user, self.user)
            self.assertEqual(ticket.event, self.event)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TicketServiceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
