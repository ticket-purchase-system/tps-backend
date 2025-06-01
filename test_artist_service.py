import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsa_backend.settings')
django.setup()

import unittest
from django.test import TestCase
from app.services.artist_service import ArtistService
from app.models.artist import Artist

class ArtistServiceTest(TestCase):
    def setUp(self):
        self.service = ArtistService()

    def test_create_artist(self):
        artist = self.service.create_artist(
            name="Test Artist",
            genre="Jazz",
            bio="This is a test bio."
        )
        self.assertIsNotNone(artist.id)
        self.assertEqual(artist.name, "Test Artist")
        self.assertEqual(artist.genre, "Jazz")
        self.assertEqual(artist.bio, "This is a test bio.")

    def test_get_artist(self):
        artist = self.service.create_artist(
            name="Another Artist",
            genre="Rock",
            bio="Another bio."
        )
        fetched_artist = self.service.get_artist(artist.id)
        self.assertIsNotNone(fetched_artist)
        self.assertEqual(fetched_artist.id, artist.id)

    def test_get_artists(self):
        Artist.objects.all().delete()  # Clean slate

        self.service.create_artist(name="A1", genre="Pop")
        self.service.create_artist(name="A2", genre="Rock")
        self.service.create_artist(name="A3", genre="Jazz")

        artists = self.service.get_artists()
        self.assertEqual(len(artists), 3)

    def test_get_artists_with_filters(self):
        Artist.objects.all().delete()

        self.service.create_artist(name="Filter Artist", genre="Electronic")
        self.service.create_artist(name="Another Artist", genre="Electronic")
        self.service.create_artist(name="Different Genre", genre="Hip Hop")

        # Filter by genre
        electronic_artists = self.service.get_artists(genre="Electronic")
        self.assertEqual(len(electronic_artists), 2)

        # Filter by query (name contains)
        name_filtered = self.service.get_artists(query="Filter")
        self.assertEqual(len(name_filtered), 1)
        self.assertEqual(name_filtered[0].name, "Filter Artist")

    def test_update_artist(self):
        artist = self.service.create_artist(name="Old Name", genre="Old Genre", bio="Old bio.")

        updated_artist = self.service.update_artist(
            artist_id=artist.id,
            name="New Name",
            genre="New Genre",
            bio="New bio."
        )
        self.assertIsNotNone(updated_artist)
        self.assertEqual(updated_artist.name, "New Name")
        self.assertEqual(updated_artist.genre, "New Genre")
        self.assertEqual(updated_artist.bio, "New bio.")

    def test_update_nonexistent_artist(self):
        result = self.service.update_artist(artist_id=9999, name="Ghost Artist")
        self.assertIsNone(result)

    def test_delete_artist(self):
        artist = self.service.create_artist(name="Delete Me", genre="Temp")

        result = self.service.delete_artist(artist.id)
        self.assertTrue(result)
        # Verify deletion
        deleted_artist = self.service.get_artist(artist.id)
        self.assertIsNone(deleted_artist)

    def test_delete_nonexistent_artist(self):
        result = self.service.delete_artist(artist_id=9999)
        self.assertFalse(result)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ArtistServiceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
