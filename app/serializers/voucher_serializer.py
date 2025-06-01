from rest_framework import serializers
from app.models.voucher import Voucher
from app.serializers.user_serializer import UserSerializer

class VoucherSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(required=False)
    owner_details = UserSerializer(source='owner', read_only=True)
    
    class Meta:
        model = Voucher
        fields = [
            'id', 'code', 'amount', 'initial_amount', 'currency_code', 
            'status', 'created_at', 'expires_at', 'owner_id', 'owner_details',
            'sent_to', 'sent_at'
        ]
        read_only_fields = ['id', 'code', 'created_at']
        
class VoucherPurchaseSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    currency_code = serializers.CharField(max_length=3, default='PLN')
    
class VoucherRedeemSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)
    
class VoucherSendSerializer(serializers.Serializer):
    recipient_email = serializers.EmailField()
    recipient_name = serializers.CharField(max_length=100, required=False)
    message = serializers.CharField(max_length=500, required=False)
    
class VoucherApplySerializer(serializers.Serializer):
    voucher_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01) 