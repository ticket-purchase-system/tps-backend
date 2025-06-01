import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsa_backend.settings')
django.setup()

import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from app.services.user_service import UserService

class UserServiceTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'securepass123'
        }

    def test_create_user(self):
        user = UserService.create_user(self.user_data)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, self.user_data['username'])

    def test_create_user_duplicate_username(self):
        UserService.create_user(self.user_data)
        with self.assertRaises(ValidationError):
            UserService.create_user(self.user_data)

    def test_create_user_missing_username(self):
        bad_data = {
            'password': 'pass'
        }
        with self.assertRaises(ValidationError):
            UserService.create_user(bad_data)

    def test_update_user(self):
        user = UserService.create_user(self.user_data)
        updated_data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }

        updated_user = UserService.update_user(user.id, updated_data)
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'User')

    def test_update_nonexistent_user(self):
        with self.assertRaises(ValidationError):
            UserService.update_user(user_id=9999, updated_data={'first_name': 'Ghost'})

    def test_search_users(self):
        UserService.create_user({'username': 'alice', 'password': 'pass1'})
        UserService.create_user({'username': 'bob', 'password': 'pass2'})
        UserService.create_user({'username': 'carol', 'password': 'pass3'})

        result = UserService.search_users('a')
        usernames = [user.username for user in result]

        self.assertIn('alice', usernames)
        self.assertIn('carol', usernames)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(UserServiceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
