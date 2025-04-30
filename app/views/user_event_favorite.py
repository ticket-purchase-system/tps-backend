from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth.models import User
from app.models import Event, AppUser
from app.models.user_event_favorite import UserEventFavorite


class UserEventFavoriteViewSet(viewsets.ViewSet):
    """
    Viewset for handling user event favorites (mark and unmark).
    """

    @action(detail=False, methods=['post'], url_path='mark_favorite')
    def mark_favorite(self, request):
        """
        Custom endpoint to mark an event as a favorite for a user.
        """
        user_id = request.data.get('user_id')
        event_id = request.data.get('event_id')

        print(user_id)
        print(event_id)

        try:
            app_user = AppUser.objects.get(pk=user_id)
            user = app_user.user
            event = Event.objects.get(id=event_id)

            # Add defaults parameter to set is_favorite to True
            favorite, created = UserEventFavorite.objects.get_or_create(
                user=user,
                event=event,
                defaults={'is_favorite': True}  # Set default value when creating
            )

            # If the object already exists but is_favorite is False, update it
            if not created and not favorite.is_favorite:
                favorite.is_favorite = True
                favorite.save()
                return Response({"detail": "Event marked as favorite."}, status=200)
            elif not created:
                return Response({"detail": "Event is already marked as favorite."}, status=400)

            return Response({"detail": "Event marked as favorite."}, status=201)
        except AppUser.DoesNotExist:
            return Response({"detail": "AppUser not found."}, status=400)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=400)
        except Exception as e:
            print(e)
            return Response({"detail": f"An error occurred: {str(e)}"}, status=500)

    @action(detail=False, methods=['post'], url_path='remove_favorite')
    def remove_favorite(self, request):
        """
        Custom endpoint to remove an event from favorites for a user.
        """
        user_id = request.data.get('user_id')
        event_id = request.data.get('event_id')

        try:
            app_user = AppUser.objects.get(pk=user_id)
            user = app_user.user
            event = Event.objects.get(id=event_id)
            favorite = UserEventFavorite.objects.filter(user=user, event=event).first()
            if not favorite:
                return Response({"detail": "Event is not marked as favorite."}, status=400)
            favorite.delete()
            return Response({"detail": "Event removed from favorites."}, status=200)
        except Exception as e:
            print(e)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_favorites(self, request, user_id=None):
        """
        Get all events marked as favorite by a user.
        """
        try:
            appUser = AppUser.objects.get(pk=user_id)
            user = appUser.user
            favorites = UserEventFavorite.objects.filter(user=user)
            event_ids = [favorite.event.id for favorite in favorites]
            return Response(event_ids, status=200)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=400)