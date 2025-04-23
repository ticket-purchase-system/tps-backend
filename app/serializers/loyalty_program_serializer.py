from rest_framework import serializers
from app.models import LoyaltyProgram, AppUser

class LoyaltyProgramSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = LoyaltyProgram
        fields = [
            'id', 'user', 'username', 'join_date', 'points', 
            'tier', 'is_active', 'preferences'
        ]
        read_only_fields = ['id', 'join_date', 'points', 'tier']
    
    def get_username(self, obj):
        return obj.user.user.username if obj.user and obj.user.user else None 