from django.db import models
from app.models import AppUser

class LoyaltyProgram(models.Model):
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE, related_name='loyalty_program')
    join_date = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    is_active = models.BooleanField(default=True)
    preferences = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user} - {self.tier} ({self.points} points)" 