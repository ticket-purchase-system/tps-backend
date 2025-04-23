from django.contrib.auth.models import User
from django.db import models

from app.models.artist import Artist

class Event(models.Model):
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    date = models.DateTimeField()
    start_hour = models.TimeField(null=True, blank=True)
    end_hour = models.TimeField(null=True, blank=True)
    place = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seats_no = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    artists = models.ManyToManyField(Artist, related_name='events')

    def __str__(self):
        return self.title