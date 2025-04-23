from app.models.artist import Artist
from app.repositories.base_repository import BaseRepository
from django.db.models import Q


class ArtistRepository(BaseRepository):
    model = Artist

    def get_artists_by_ids(self, ids):
        """Get artists by a list of IDs"""
        return self.model.objects.filter(id__in=ids)

    def search_artists(self, query=None, genre=None):
        """Search for artists with optional filtering"""
        filters = Q()

        if query:
            filters &= (Q(name__icontains=query) | Q(bio__icontains=query))

        if genre:
            filters &= Q(genre__icontains=genre)

        return self.model.objects.filter(filters).order_by('name')