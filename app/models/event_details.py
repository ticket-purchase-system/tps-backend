from django.db import models
from app.models import Event

def event_rules_path(instance, filename):
    return f'event_rules/{instance.event.id}/{filename}'

class EventDetails(models.Model):
    event = models.ForeignKey(Event, related_name="details", on_delete=models.CASCADE)
    rules_pdf = models.FileField(upload_to=event_rules_path, blank=True, null=True)
    rules_text = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=255, blank=True, null=True)
    rules = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Event Detail"
        verbose_name_plural = "Event Details"

    def __str__(self):
        return f"Details for {self.event.title}"


