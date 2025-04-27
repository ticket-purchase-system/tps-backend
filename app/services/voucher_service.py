from django.core.exceptions import ValidationError
from django.utils import timezone
from app.repositories.voucher_repository import VoucherRepository
from app.repositories.user_repository import UserRepository
from datetime import timedelta
import uuid

class VoucherService:
    def __init__(self):
        self.voucher_repository = VoucherRepository()
        self.user_repository = UserRepository()
    
    def purchase_voucher(self, user_id, amount, currency_code='PLN'):
        """Purchase a new voucher for a user"""
        if amount <= 0:
            raise ValidationError("Voucher amount must be positive")
            
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
        
        # Create expiration date (6 months from now)
        expires_at = timezone.now() + timedelta(days=180)
        
        # Generate a unique code
        code = f"GIFT-{uuid.uuid4().hex[:8].upper()}"
        
        # Create the voucher
        voucher_data = {
            'code': code,
            'amount': amount,
            'initial_amount': amount,
            'currency_code': currency_code,
            'status': 'active',
            'expires_at': expires_at,
            'owner': user
        }
        
        voucher = self.voucher_repository.create(**voucher_data)
        return voucher
    
    def validate_voucher(self, code):
        """Validate if a voucher is valid and return its amount"""
        voucher = self.voucher_repository.get_by_code(code)
        
        if not voucher:
            raise ValidationError("Voucher not found")
            
        if voucher.status != 'active':
            raise ValidationError("Voucher is not active")
            
        if voucher.is_expired():
            voucher.status = 'expired'
            voucher.save()
            raise ValidationError("Voucher has expired")
            
        return voucher
    
    def redeem_voucher(self, code, user_id):
        """Redeem a voucher by code and assign it to a user"""
        voucher = self.validate_voucher(code)
        
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
            
        # If voucher already belongs to this user, return an error message
        if voucher.owner_id == user_id:
            raise ValidationError("You already own this voucher")
            
        # If voucher was sent to someone, check if the current user is the recipient
        if voucher.sent_to and user.user.email != voucher.sent_to:
            raise ValidationError("This voucher was sent to a different email address")
            
        # Transfer ownership to the new user
        voucher.owner = user
        voucher.save()
        
        return voucher
    
    def send_voucher(self, voucher_id, recipient_email, recipient_name=None, message=None):
        """Send a voucher as a gift to someone else"""
        voucher = self.voucher_repository.get_by_id(voucher_id)
        
        if not voucher:
            raise ValidationError("Voucher not found")
            
        if voucher.status != 'active':
            raise ValidationError("Cannot send voucher that is not active")
            
        if voucher.sent_to:
            raise ValidationError("Voucher has already been sent")
            
        # Update voucher with sent information
        voucher.sent_to = recipient_email
        voucher.sent_at = timezone.now()
        voucher.save()
        
        # In a real implementation, you would send an actual email here
        # For now, just update the voucher record
        
        return voucher
    
    def apply_voucher_to_purchase(self, voucher_id, purchase_amount):
        """Apply a voucher to a purchase, updating its remaining amount or marking as used"""
        voucher = self.voucher_repository.get_by_id(voucher_id)
        
        if not voucher:
            raise ValidationError("Voucher not found")
            
        if voucher.status != 'active':
            raise ValidationError("Voucher is not active")
            
        if voucher.is_expired():
            voucher.status = 'expired'
            voucher.save()
            raise ValidationError("Voucher has expired")
            
        # Calculate how much of the voucher to use
        voucher_amount = float(voucher.amount)
        amount_to_use = min(voucher_amount, purchase_amount)
        remaining = voucher_amount - amount_to_use
        
        # Update the voucher
        if remaining <= 0:
            voucher.amount = 0
            voucher.status = 'used'
        else:
            voucher.amount = remaining
            
        voucher.save()
        
        return {
            'voucher': voucher,
            'amount_used': amount_to_use,
            'remaining': remaining
        }
    
    def get_user_vouchers(self, user_id):
        """Get all vouchers for a user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
            
        vouchers = self.voucher_repository.get_user_vouchers(user_id)
        
        # Update status for any expired vouchers
        for voucher in vouchers:
            if voucher.status == 'active' and voucher.is_expired():
                voucher.status = 'expired'
                voucher.save()
                
        return vouchers 