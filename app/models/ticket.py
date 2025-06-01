from django.db import models
from django.conf import settings
from app.models.event import Event
from django.contrib.auth.models import User

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seat = models.CharField(max_length=10, blank=True)
    quantity = models.IntegerField(default=1)
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
