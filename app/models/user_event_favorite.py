from django.contrib.auth.models import User
from django.db import models
from app.models import Event

class UserEventFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f'{self.user.username} - {self.event.title} - Favorite: {self.is_favorite}'