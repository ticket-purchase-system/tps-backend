from django.db import models
from django.utils import timezone
from app.models.user import AppUser
import uuid

class Voucher(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency_code = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    owner = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='owned_vouchers')
    sent_to = models.EmailField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Voucher {self.code} - {self.amount} {self.currency_code}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_active(self):
        return self.status == 'active' and not self.is_expired()
    
    def save(self, *args, **kwargs):
        # Auto-generate code if not provided
        if not self.code:
            self.code = f"GIFT-{uuid.uuid4().hex[:8].upper()}"
        
        # Update status if expired
        if self.is_expired() and self.status == 'active':
            self.status = 'expired'
            
        super().save(*args, **kwargs) 