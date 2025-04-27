from app.models.voucher import Voucher
from app.repositories.base_repository import BaseRepository

class VoucherRepository(BaseRepository):
    model = Voucher
    
    def get_by_code(self, code):
        """Get a voucher by its code"""
        try:
            return self.model.objects.get(code=code)
        except self.model.DoesNotExist:
            return None
    
    def get_user_vouchers(self, user_id):
        """Get all vouchers owned by a specific user"""
        return self.model.objects.filter(owner_id=user_id)
    
    def get_active_vouchers(self, user_id):
        """Get all active vouchers owned by a specific user"""
        return self.model.objects.filter(owner_id=user_id, status='active')
    
    def mark_as_used(self, voucher_id):
        """Mark a voucher as used"""
        voucher = self.get_by_id(voucher_id)
        if voucher:
            voucher.status = 'used'
            voucher.save()
            return voucher
        return None
    
    def update_amount(self, voucher_id, new_amount):
        """Update the amount of a voucher"""
        voucher = self.get_by_id(voucher_id)
        if voucher:
            voucher.amount = new_amount
            voucher.save()
            return voucher
        return None 