from rest_framework import serializers
from app.models.event_details import EventDetails
from app.serializers.event_attachment_serializer import EventAttachmentSerializer

class EventDetailsSerializer(serializers.ModelSerializer):
    attachments = EventAttachmentSerializer(many=True, read_only=True)
    rules_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = EventDetails
        fields = ['id', 'event', 'rules_text', 'rules_pdf', 'rules_pdf_url', 'attachments']
        read_only_fields = ['id', 'rules_pdf_url', 'attachments']

    def get_rules_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.rules_pdf and hasattr(obj.rules_pdf, 'url') and request is not None:
            return request.build_absolute_uri(obj.rules_pdf.url)
        return None