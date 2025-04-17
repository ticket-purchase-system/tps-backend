from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth.models import User
from app.models import Event
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

        try:
            user = User.objects.get(id=user_id)
            event = Event.objects.get(id=event_id)
            favorite, created = UserEventFavorite.objects.get_or_create(user=user, event=event)
            if not created:
                return Response({"detail": "Event is already marked as favorite."}, status=400)
            return Response({"detail": "Event marked as favorite."}, status=201)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=400)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=400)

    @action(detail=False, methods=['post'], url_path='remove_favorite')
    def remove_favorite(self, request):
        """
        Custom endpoint to remove an event from favorites for a user.
        """
        user_id = request.data.get('user_id')
        event_id = request.data.get('event_id')

        try:
            user = User.objects.get(id=user_id)
            event = Event.objects.get(id=event_id)
            favorite = UserEventFavorite.objects.filter(user=user, event=event).first()
            if not favorite:
                return Response({"detail": "Event is not marked as favorite."}, status=400)
            favorite.delete()
            return Response({"detail": "Event removed from favorites."}, status=200)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=400)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=400)