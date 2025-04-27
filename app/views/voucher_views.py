from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from app.models.voucher import Voucher
from app.serializers.voucher_serializer import (
    VoucherSerializer, 
    VoucherPurchaseSerializer, 
    VoucherRedeemSerializer,
    VoucherSendSerializer,
    VoucherApplySerializer
)
from app.services.voucher_service import VoucherService

class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voucher_service = VoucherService()
    
    def get_queryset(self):
        """Restrict users to see only their own vouchers"""
        user = self.request.user
        if user.is_staff:
            return Voucher.objects.all()
        return Voucher.objects.filter(owner__user=user)
    
    @action(detail=False, methods=['get'])
    def user(self, request):
        """Get all vouchers for the current user"""
        try:
            # Get user_id from the associated AppUser model
            user = request.user
            print(f"Getting vouchers for user {user.username} (ID: {user.id})")
            
            try:
                appuser = user.appuser
                print(f"AppUser found: {appuser.id} ({appuser.first_name} {appuser.last_name})")
            except Exception as e:
                print(f"Error getting AppUser: {e}")
                return Response({'error': 'User profile not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get all vouchers to debug
            all_vouchers = Voucher.objects.all()
            print(f"Total vouchers in system: {all_vouchers.count()}")
            for v in all_vouchers:
                print(f"Voucher ID: {v.id}, Code: {v.code}, Owner: {v.owner_id}")
            
            user_id = appuser.id
            vouchers = self.voucher_service.get_user_vouchers(user_id)
            print(f"Found {len(vouchers)} vouchers for user {user_id}")
            
            serializer = self.get_serializer(vouchers, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            print(f"Validation error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def purchase(self, request):
        """Purchase a new voucher"""
        serializer = VoucherPurchaseSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"Invalid purchase data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Get user_id from the associated AppUser model
            user = request.user
            print(f"Purchasing voucher for user {user.username} (ID: {user.id})")
            
            try:
                appuser = user.appuser
                print(f"AppUser found: {appuser.id} ({appuser.first_name} {appuser.last_name})")
            except Exception as e:
                print(f"Error getting AppUser: {e}")
                return Response({'error': 'User profile not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = appuser.id
            amount = serializer.validated_data['amount']
            currency_code = serializer.validated_data.get('currency_code', 'PLN')
            
            print(f"Creating voucher: amount={amount}, currency={currency_code}")
            
            voucher = self.voucher_service.purchase_voucher(
                user_id=user_id,
                amount=amount,
                currency_code=currency_code
            )
            
            print(f"Voucher created successfully: ID={voucher.id}, Code={voucher.code}")
            
            result_serializer = self.get_serializer(voucher)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            print(f"Validation error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def validate(self, request, code=None):
        """Validate a voucher code"""
        code = self.kwargs.get('code', request.query_params.get('code'))
        if not code:
            return Response({'error': 'Voucher code is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            voucher = self.voucher_service.validate_voucher(code)
            return Response({
                'valid': True,
                'amount': voucher.amount,
                'currency_code': voucher.currency_code
            })
        except ValidationError as e:
            return Response({'valid': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'valid': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def redeem(self, request):
        """Redeem a voucher code"""
        serializer = VoucherRedeemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Get user_id from the associated AppUser model
            try:
                appuser = request.user.appuser
                user_id = appuser.id
            except Exception as e:
                print(f"Error getting AppUser: {e}")
                return Response({'error': 'User profile not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the user already has this voucher code
            code = serializer.validated_data['code']
            user_vouchers = self.voucher_service.get_user_vouchers(user_id)
            if any(v.code == code for v in user_vouchers):
                return Response({'success': False, 'error': 'You already own this voucher'}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # Try to redeem the voucher
            voucher = self.voucher_service.redeem_voucher(
                code=code,
                user_id=user_id
            )
            
            result_serializer = self.get_serializer(voucher)
            return Response({
                'success': True,
                'amount': voucher.amount,
                'voucher': result_serializer.data
            })
        except ValidationError as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error in redeem endpoint: {e}")
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a voucher as a gift"""
        serializer = VoucherSendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            voucher = self.voucher_service.send_voucher(
                voucher_id=pk,
                recipient_email=serializer.validated_data['recipient_email'],
                recipient_name=serializer.validated_data.get('recipient_name'),
                message=serializer.validated_data.get('message')
            )
            
            result_serializer = self.get_serializer(voucher)
            return Response(result_serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def apply(self, request):
        """Apply a voucher to a purchase"""
        serializer = VoucherApplySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            result = self.voucher_service.apply_voucher_to_purchase(
                voucher_id=serializer.validated_data['voucher_id'],
                purchase_amount=serializer.validated_data['amount']
            )
            
            voucher_serializer = self.get_serializer(result['voucher'])
            return Response({
                'success': True,
                'amount_used': result['amount_used'],
                'remaining': result['remaining'],
                'voucher': voucher_serializer.data
            })
        except ValidationError as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 