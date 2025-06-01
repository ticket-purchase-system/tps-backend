from django.db import models
from django.contrib.auth.models import User
from .event import Event

class EventPhoto(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='event_photos/')
    caption = models.TextField(blank=True, max_length=500)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Photo for {self.event.title} - {self.uploaded_at.strftime('%Y-%m-%d')}"

    @property
    def url(self):
        """Get the URL of the image"""
        if self.image:
            return self.image.url
        return None