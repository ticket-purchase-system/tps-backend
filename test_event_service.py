import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsa_backend.settings') 
django.setup()

import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from app.services.event_service import EventService
from app.models.event import Event
from app.models.artist import Artist


class EventServiceTest(TestCase):
    def setUp(self):
        self.service = EventService()
        self.user = User.objects.create_user(username='testuser', password='123')
        self.artist = Artist.objects.create(name="Test Artist", genre="Jazz", bio="Test bio")

    def test_create_event(self):
        event = self.service.create_event(
            title='Test Event',
            type='Concert',
            date=timezone.now(),
            price=100.00,
            description='This is a test event.',
            created_by=self.user,
            start_hour='18:00',
            end_hour='20:00',
            place='Main Hall',
            seats_no=50,
            artists=[self.artist.id]
        )

        self.assertIsNotNone(event.id)
        self.assertEqual(event.title, 'Test Event')
        self.assertIn(self.artist, event.artists.all())

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
            'seats_no': seats_no
        }

        update_data = {k: v for k, v in update_data.items() if v is not None}

        updated_event = self.event_repository.update(event, **update_data)

        if artists:
            self.event_repository.add_artists_to_event(updated_event, artists)

        return updated_event


    def test_get_event(self):
        event = self.service.create_event(
            title='Event for get',
            type='Lecture',
            date=timezone.now(),
            price=0,
            description='To be fetched',
            created_by=self.user
        )

        result = self.service.get_event(event.id)
        self.assertEqual(result['event'].id, event.id)
        self.assertIsNone(result['details'])

    def test_get_events(self):
        Event.objects.all().delete() 
        
        self.service.create_event(
            title='E1',
            type='Lecture',
            date=timezone.now(),
            price=20,
            description='First',
            created_by=self.user
        )
        self.service.create_event(
            title='E2',
            type='Lecture',
            date=timezone.now(),
            price=30,
            description='Second',
            created_by=self.user
        )

        results = self.service.get_events()
        self.assertEqual(len(results), 2)


    def test_update_nonexistent_event(self):
        result = self.service.update_event(event_id=999, title="Ghost")
        self.assertIsNone(result)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EventServiceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
