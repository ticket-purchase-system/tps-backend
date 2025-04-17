from app.models import Event
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from app.models.user_event_favorite import UserEventFavorite

class UserEventFavoriteService:
    @staticmethod
    def mark_favorite(user: User, event_id: int, is_favorite: bool):
        """
        Mark an event as a favorite or remove it from favorites for the user.
        """
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise ValidationError("Event not found")

        favorite, created = UserEventFavorite.objects.update_or_create(
            user=user,
            event=event,
            defaults={'is_favorite': is_favorite},
        )
        return favorite

    @staticmethod
    def get_user_favorites(user: User):
        """
        Get all the events that are marked as favorites for the user.
        """
        return UserEventFavorite.objects.filter(user=user, is_favorite=True)

    @staticmethod
    def remove_favorite(user: User, event_id: int):
        """
        Remove an event from the user's favorites.
        """
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise ValidationError("Event not found")

        favorite = UserEventFavorite.objects.filter(user=user, event=event)
        if favorite.exists():
            favorite.delete()
        else:
            raise ValidationError("Event not marked as favorite by user")
