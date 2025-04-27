from rest_framework import serializers
from app.models import EventAttachment

class EventAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = EventAttachment
        fields = ['id', 'title', 'description', 'file', 'file_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url') and request is not None:
            return request.build_absolute_uri(obj.file.url)
        return None