from django.db import models
from app.models import Event

class EventDetails(models.Model):
    event = models.ForeignKey(Event, related_name="details", on_delete=models.CASCADE)
    venue = models.CharField(max_length=255)
    rules = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Details for {self.event.title} - {self.venue}"
