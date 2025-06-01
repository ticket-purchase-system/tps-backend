import os
import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from urllib3 import request
from app.models import Review
from app.serializers.event_serializer import EventSerializer
from app.services.event_service import EventService
from app.models.event import Event
from app.models.artist import Artist
from app.models.user import AppUser
from django.utils import timezone


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    event_service = EventService()

    @action(detail=False, methods=['post'])
    def create_event(self, request):
        """Custom endpoint to create an event."""
        title = request.data.get('title')
        type = request.data.get('type', 'CONCERT')  # Default type
        date = request.data.get('date')
        price = request.data.get('price')
        description = request.data.get('description')
        user_id = request.data.get('created_by')

        # New fields
        start_hour = request.data.get('start_hour')
        end_hour = request.data.get('end_hour')
        place = request.data.get('place')
        seats_no = request.data.get('seats_no')
        artist_ids = request.data.get('artists', [])

        artists = []
        if artist_ids:
            artists = Artist.objects.filter(id__in=artist_ids)

        print(request.data)
        try:
            created_by = AppUser.objects.get(id=user_id)
            event = self.event_service.create_event(
                title, type, date, price, description, created_by.user,
                start_hour, end_hour, place, seats_no, artists
            )
            serializer = self.get_serializer(event)
            return Response(serializer.data, status=201)
        except AppUser.DoesNotExist:
            print("User not found!")
            return Response({'error': 'User not found'}, status=400)

        except Exception as e:
            print("Unexpected error:", e)
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['put'])
    def update_event(self, request, pk=None):
        """Custom endpoint to update an event."""
        title = request.data.get('title')
        type = request.data.get('type')
        date = request.data.get('date')
        price = request.data.get('price')
        description = request.data.get('description')

        # New fields
        start_hour = request.data.get('start_hour')
        end_hour = request.data.get('end_hour')
        place = request.data.get('place')
        seats_no = request.data.get('seats_no')
        artist_ids = request.data.get('artists')

        artists = None
        if artist_ids:
            artists = Artist.objects.filter(id__in=artist_ids)

        event = self.event_service.update_event(
            pk, title, type, date, price, description,
            start_hour, end_hour, place, seats_no, artists
        )

        if event:
            serializer = self.get_serializer(event)
            return Response(serializer.data)
        else:
            return Response({'error': 'Event not found'}, status=404)

    def list(self, request, *args, **kwargs):
        """List all events, optionally filtered by query or date"""
        query = request.query_params.get('query', '')
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        event_data = self.event_service.get_events(query, start_date, end_date)

        events = [
            {
                'event': EventSerializer(event['event']).data
            }
            for event in event_data
        ]

        return Response(events)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single event by ID with details"""
        pk = kwargs['pk']
        event_data = self.event_service.get_event(pk)

        if event_data:
            event_serializer = EventSerializer(event_data['event'])
            event_details = event_data['details']

            return Response({
                'event': event_serializer.data,
                'details': {
                    'location': event_details.location if event_details else None,
                    'rules': event_details.rules if event_details else None,
                    'max_attendees': event_details.max_attendees if event_details else None,
                    'additional_info': event_details.additional_info if event_details else None
                }
            })
        return Response({"detail": "Event not found"}, status=404)

    @action(detail=False, methods=['get'])
    def past_events_with_reviews(self, request):
        """Endpoint to fetch past events with all available reviews and photos"""
        from django.utils import timezone
        import logging

        logger = logging.getLogger(__name__)

        query = request.query_params.get('query', '')
        limit = request.query_params.get('limit', None)

        try:
            if limit:
                limit = int(limit)
        except ValueError:
            return Response({'error': 'Invalid limit parameter'}, status=400)

        try:
            current_datetime = timezone.now()
            logger.info(f"Current datetime: {current_datetime}")

            past_events = Event.objects.filter(date__lt=current_datetime)
            logger.info(f"Found {past_events.count()} past events")

            if query:
                past_events = past_events.filter(title__icontains=query)
                logger.info(f"After query filter: {past_events.count()} events")

            past_events = past_events.order_by('-date')

            if limit:
                past_events = past_events[:limit]

            events_with_reviews = []

            for event in past_events:
                logger.info(f"Processing event: {event.id} - {event.title}")

                try:
                    reviews = Review.objects.filter(
                        order__orderproduct__product__event=event
                    ).distinct()

                    logger.info(f"Found {reviews.count()} reviews for event {event.id}")

                    review_data = []
                    for review in reviews:
                        review_data.append({
                            'id': review.id,
                            'numberOfStars': review.numberOfStars,
                            'comment': review.comment,
                            'date': review.date,
                            'rating': review.rating
                        })

                    photos = []
                    try:
                        try:
                            from app.models.event_photo import EventPhoto
                            event_photos = EventPhoto.objects.filter(event=event).order_by('-uploaded_at')
                            for photo in event_photos:
                                photo_url = photo.url
                                if photo_url and not photo_url.startswith('http'):
                                    photo_url = f"http://localhost:8000{photo_url}"
                                elif photo_url and photo_url.startswith('/'):
                                    photo_url = f"http://localhost:8000{photo_url}"

                                photos.append({
                                    'id': photo.id,
                                    'url': photo_url,
                                    'caption': photo.caption,
                                    'uploaded_at': photo.uploaded_at.isoformat() if photo.uploaded_at else None
                                })
                            logger.info(f"Found {len(photos)} photos for event {event.id} using EventPhoto model")

                        except ImportError:
                            if hasattr(event, 'photos') and event.photos:
                                if isinstance(event.photos, str):
                                    import json
                                    photos_data = json.loads(event.photos)
                                elif isinstance(event.photos, list):
                                    photos_data = event.photos
                                elif hasattr(event.photos, 'all'):
                                    photos_data = []
                                    for photo in event.photos.all():
                                        photo_url = photo.url if hasattr(photo,
                                                                         'url') and photo.url else photo.image.url if hasattr(
                                            photo, 'image') and photo.image else None

                                        if photo_url and not photo_url.startswith('http'):
                                            photo_url = f"http://localhost:8000{photo_url}"
                                        elif photo_url and photo_url.startswith('/'):
                                            photo_url = f"http://localhost:8000{photo_url}"

                                        photos_data.append({
                                            'id': photo.id,
                                            'url': photo_url,
                                            'caption': getattr(photo, 'caption', ''),
                                            'uploaded_at': getattr(photo, 'uploaded_at', None)
                                        })

                                for photo_data in photos_data:
                                    if isinstance(photo_data, dict):
                                        photo_url = photo_data.get('url', '')
                                        if photo_url and not photo_url.startswith('http'):
                                            photo_data['url'] = f"http://localhost:8000{photo_url}"
                                        elif photo_url and photo_url.startswith('/'):
                                            photo_data['url'] = f"http://localhost:8000{photo_url}"
                                        photos.append(photo_data)

                            logger.info(f"Found {len(photos)} photos for event {event.id} using JSON field")

                    except Exception as photo_error:
                        logger.warning(f"Error loading photos for event {event.id}: {str(photo_error)}")
                        photos = []
                    event_serializer = EventSerializer(event)

                    events_with_reviews.append({
                        'event': event_serializer.data,
                        'reviews': review_data,
                        'photos': photos,
                        'review_count': len(review_data),
                        'photo_count': len(photos)
                    })

                except Exception as e:
                    logger.error(f"Error processing event {event.id}: {str(e)}")
                    continue

            logger.info(f"Returning {len(events_with_reviews)} events with reviews")

            return Response({
                'past_events_with_reviews': events_with_reviews,
                'count': len(events_with_reviews)
            })

        except Exception as e:
            logger.error(f"Error in past_events_with_reviews: {str(e)}")
            return Response({'error': f'Internal server error: {str(e)}'}, status=500)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request, pk=None):
        """Upload a single photo for a specific event."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            event = Event.objects.get(id=pk)
            logger.info(f"Found event: {event.id}")
        except Event.DoesNotExist:
            logger.error(f"Event with id {pk} not found")
            return Response({'error': 'Event not found'}, status=404)

        photo_file = request.FILES.get('photo')
        caption = request.data.get('caption', '')

        logger.info(f"Photo file: {photo_file}")
        logger.info(f"Caption: {caption}")

        if not photo_file:
            return Response({'error': 'No photo provided'}, status=400)

        try:
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(photo_file, 'content_type') and photo_file.content_type not in allowed_types:
                return Response({
                    'error': 'Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.'
                }, status=400)

            max_size = 5 * 1024 * 1024  # 5MB
            if hasattr(photo_file, 'size') and photo_file.size > max_size:
                return Response({
                    'error': 'File too large. Maximum size is 5MB.'
                }, status=400)

            file_extension = os.path.splitext(photo_file.name)[1] if photo_file.name else '.jpg'
            unique_filename = f"event_{event.id}_{uuid.uuid4().hex}{file_extension}"
            file_path = f"event_photos/{unique_filename}"

            logger.info(f"Saving file to: {file_path}")

            try:
                saved_path = default_storage.save(file_path, ContentFile(photo_file.read()))
                logger.info(f"File saved successfully to: {saved_path}")
            except Exception as storage_error:
                logger.error(f"Storage error: {str(storage_error)}")
                return Response({'error': f'Failed to save file: {str(storage_error)}'}, status=500)

            photo_data = {
                'url': default_storage.url(saved_path),
                'caption': caption,
                'uploaded_at': timezone.now().isoformat()
            }

            try:
                from app.models.event_photo import EventPhoto
                logger.info("Using EventPhoto model")

                uploaded_by = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    uploaded_by = request.user

                photo = EventPhoto.objects.create(
                    event=event,
                    image=saved_path,
                    caption=caption,
                    uploaded_by=uploaded_by
                )
                photo_data['id'] = photo.id
                logger.info(f"EventPhoto created with id: {photo.id}")

            except (ImportError, AttributeError) as model_error:
                logger.info(f"EventPhoto model not available, using JSON field: {str(model_error)}")

                try:
                    if not hasattr(event, 'photos'):
                        logger.warning("Event model doesn't have 'photos' field")
                        return Response({'error': 'Photo storage not properly configured'}, status=500)

                    if event.photos is None:
                        event.photos = []
                    elif isinstance(event.photos, str):
                        import json
                        try:
                            event.photos = json.loads(event.photos) if event.photos else []
                        except json.JSONDecodeError:
                            event.photos = []

                    photo_data['id'] = len(event.photos) + 1
                    event.photos.append(photo_data)
                    event.save()
                    logger.info("Photo saved to JSON field")

                except Exception as json_error:
                    logger.error(f"JSON field error: {str(json_error)}")
                    try:
                        default_storage.delete(saved_path)
                    except:
                        pass
                    return Response({'error': f'Failed to save photo data: {str(json_error)}'}, status=500)

            return Response({
                'message': 'Photo uploaded successfully',
                'photo': photo_data
            }, status=201)

        except Exception as e:
            logger.error(f"Unexpected error in upload_photo: {str(e)}")
            logger.exception("Full traceback:")
            return Response({'error': f'Internal server error: {str(e)}'}, status=500)

    @action(detail=True, methods=['delete'])
    def delete_photo(self, request, pk=None):
        """Delete a specific photo from an event."""
        try:
            event = Event.objects.get(id=pk)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=404)

        photo_id = request.data.get('photo_id')
        if not photo_id:
            return Response({'error': 'Photo ID is required'}, status=400)

        try:
            try:
                from app.models.event_photo import EventPhoto
                photo = EventPhoto.objects.get(id=photo_id, event=event)

                if photo.image:
                    default_storage.delete(photo.image.name)

                photo.delete()

            except ImportError:
                if hasattr(event, 'photos') and event.photos:
                    if isinstance(event.photos, str):
                        import json
                        photos = json.loads(event.photos)
                    else:
                        photos = event.photos

                    photo_to_remove = None
                    for i, photo in enumerate(photos):
                        if photo.get('id') == int(photo_id):
                            photo_to_remove = i
                            if 'url' in photo:
                                file_path = photo['url'].replace(default_storage.base_url, '')
                                default_storage.delete(file_path)
                            break

                    if photo_to_remove is not None:
                        photos.pop(photo_to_remove)
                        event.photos = photos
                        event.save()
                    else:
                        return Response({'error': 'Photo not found'}, status=404)

            return Response({'message': 'Photo deleted successfully'}, status=200)

        except Exception as e:
            return Response({'error': f'Failed to delete photo: {str(e)}'}, status=500)