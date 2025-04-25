from rest_framework import serializers
from app.models import EventAttachment

class EventAttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttachment
        fields = ['id', 'title', 'description', 'file']
        read_only_fields = ['id']

    def validate_file(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return value