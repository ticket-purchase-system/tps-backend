from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from app.models.artist import Artist
from app.serializers.artist_serializer import ArtistSerializer
from app.services.artist_service import ArtistService

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    artist_service = ArtistService()

    def list(self, request, *args, **kwargs):
        """List all artists, with optional filtering"""
        query = request.query_params.get('query', None)
        genre = request.query_params.get('genre', None)

        artists = self.artist_service.get_artists(query, genre)
        serializer = self.get_serializer(artists, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get a specific artist by ID"""
        pk = kwargs.get('pk')
        artist = self.artist_service.get_artist(pk)

        if not artist:
            return Response({"detail": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(artist)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new artist"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        artist = self.artist_service.create_artist(
            name=serializer.validated_data['name'],
            genre=serializer.validated_data.get('genre'),
            bio=serializer.validated_data.get('bio')
        )

        result_serializer = self.get_serializer(artist)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update an existing artist"""
        pk = kwargs.get('pk')
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        artist = self.artist_service.update_artist(
            artist_id=pk,
            name=serializer.validated_data.get('name'),
            genre=serializer.validated_data.get('genre'),
            bio=serializer.validated_data.get('bio')
        )

        if not artist:
            return Response({"detail": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        result_serializer = self.get_serializer(artist)
        return Response(result_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete an artist"""
        pk = kwargs.get('pk')
        success = self.artist_service.delete_artist(pk)

        if not success:
            return Response({"detail": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def genres(self, request):
        """Get a list of unique genres"""
        genres = Artist.objects.exclude(genre__isnull=True).exclude(genre='').values_list('genre', flat=True).distinct().order_by('genre')
        return Response(list(genres))