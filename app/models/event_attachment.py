from django.db import models
from app.models.event_details import EventDetails

def event_attachment_path(instance, filename):
    return f'event_attachments/{instance.event.id}/{filename}'

class EventAttachment(models.Model):
    event_details = models.ForeignKey(EventDetails, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to=event_attachment_path)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title