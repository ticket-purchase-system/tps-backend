from django.core.files.storage import default_storage
from django.db import transaction
from app.models import Event, EventDetails, EventAttachment

class EventDetailsService:
    @staticmethod
    def get_event_details(event_id):
        """
        Get event details for a specific event
        """
        try:
            event = Event.objects.get(id=event_id)
            details, created = EventDetails.objects.get_or_create(event=event)
            return details
        except Event.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def update_event_rules(event_id, rules_pdf=None, rules_text=None):
        """
        Update event rules with PDF and/or text
        """
        details = EventDetailsService.get_event_details(event_id)
        if not details:
            return None

        if rules_pdf:
            if details.rules_pdf:
                # Delete old file if it exists
                if default_storage.exists(details.rules_pdf.name):
                    default_storage.delete(details.rules_pdf.name)
            details.rules_pdf = rules_pdf

        if rules_text is not None:  # Allow empty string
            details.rules_text = rules_text

        details.save()
        return details

    @staticmethod
    @transaction.atomic
    def add_attachment(event_id, file, title, description=None):
        """
        Add an attachment to event details
        """
        details = EventDetailsService.get_event_details(event_id)
        if not details:
            return None

        attachment = EventAttachment(
            event_details=details,
            file=file,
            title=title,
            description=description
        )
        attachment.save()
        return attachment

    @staticmethod
    def remove_attachment(attachment_id):
        """
        Remove an attachment
        """
        try:
            attachment = EventAttachment.objects.get(id=attachment_id)
            if default_storage.exists(attachment.file.name):
                default_storage.delete(attachment.file.name)
            attachment.delete()
            return True
        except EventAttachment.DoesNotExist:
            return False

    @staticmethod
    def get_attachments(event_id):
        """
        Get all attachments for an event
        """
        details = EventDetailsService.get_event_details(event_id)
        if not details:
            return []
        return details.attachments.all()