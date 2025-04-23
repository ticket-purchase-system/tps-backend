from rest_framework import serializers
from app.models import TechnicalIssue

class TechnicalIssueSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = TechnicalIssue
        fields = [
            'id', 'user', 'username', 'title', 'description', 
            'priority', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
    
    def get_username(self, obj):
        return obj.user.user.username if obj.user and obj.user.user else None 