from app.repositories.artist_repository import ArtistRepository


class ArtistService:
    def __init__(self):
        self.artist_repository = ArtistRepository()

    def get_artists(self, query=None, genre=None):
        """Get all artists with optional filtering"""
        if query or genre:
            return self.artist_repository.search_artists(query, genre)
        else:
            return self.artist_repository.get_all()

    def get_artist(self, artist_id):
        """Get an artist by ID"""
        return self.artist_repository.get_by_id(artist_id)

    def get_artists_by_ids(self, artist_ids):
        """Get artists by a list of IDs"""
        if not artist_ids:
            return []
        return self.artist_repository.get_artists_by_ids(artist_ids)

    def create_artist(self, name, genre=None, bio=None):
        """Create a new artist"""
        return self.artist_repository.create(
            name=name,
            genre=genre,
            bio=bio
        )

    def update_artist(self, artist_id, name=None, genre=None, bio=None):
        """Update an existing artist"""
        artist = self.artist_repository.get_by_id(artist_id)
        if not artist:
            return None

        update_data = {}
        if name is not None:
            update_data['name'] = name
        if genre is not None:
            update_data['genre'] = genre
        if bio is not None:
            update_data['bio'] = bio

        return self.artist_repository.update(artist, **update_data)

    def delete_artist(self, artist_id):
        """Delete an artist by ID"""
        artist = self.artist_repository.get_by_id(artist_id)
        if not artist:
            return False

        self.artist_repository.delete(artist)
        return True