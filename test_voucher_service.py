import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tsa_backend.settings')
django.setup()

import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from app.services.voucher_service import VoucherService
from app.models.voucher import Voucher
from app.models.user import AppUser
from django.utils import timezone
from datetime import timedelta

class VoucherServiceTest(TestCase):
    def setUp(self):
        self.service = VoucherService()

        # Create two users
        self.user1_django = User.objects.create_user(username='user1', password='123')
        self.user1 = AppUser.objects.create(user=self.user1_django, first_name='User', last_name='One')

        self.user2_django = User.objects.create_user(username='user2', password='123')
        self.user2 = AppUser.objects.create(user=self.user2_django, first_name='User', last_name='Two')

    def test_purchase_voucher(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=100)
        self.assertIsNotNone(voucher.id)
        self.assertEqual(voucher.owner, self.user1)
        self.assertEqual(voucher.amount, voucher.initial_amount)
        self.assertEqual(voucher.status, 'active')

    def test_purchase_voucher_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.service.purchase_voucher(user_id=self.user1.id, amount=-10)

    def test_validate_voucher(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=50)
        validated = self.service.validate_voucher(voucher.code)
        self.assertEqual(validated.id, voucher.id)

    def test_validate_expired_voucher(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=50)
        # Force expire
        voucher.expires_at = timezone.now() - timedelta(days=1)
        voucher.save()

        with self.assertRaises(ValidationError):
            self.service.validate_voucher(voucher.code)

    def test_redeem_voucher(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=75)

        # Make it "gifted"
        voucher.sent_to = self.user2.user.email
        voucher.save()

        redeemed = self.service.redeem_voucher(code=voucher.code, user_id=self.user2.id)
        self.assertEqual(redeemed.owner, self.user2)

    def test_redeem_voucher_same_owner(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=100)
        with self.assertRaises(ValidationError):
            self.service.redeem_voucher(code=voucher.code, user_id=self.user1.id)

    def test_redeem_wrong_email(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=100)
        voucher.sent_to = "wrong@example.com"
        voucher.save()

        with self.assertRaises(ValidationError):
            self.service.redeem_voucher(code=voucher.code, user_id=self.user2.id)

    def test_send_voucher(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=120)
        sent = self.service.send_voucher(
            voucher_id=voucher.id,
            recipient_email="gift@example.com",
            recipient_name="Gift Receiver",
            message="Happy Birthday!"
        )
        self.assertEqual(sent.sent_to, "gift@example.com")
        self.assertIsNotNone(sent.sent_at)

    def test_send_already_sent_voucher(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=80)
        voucher.sent_to = "already@example.com"
        voucher.sent_at = timezone.now()
        voucher.save()

        with self.assertRaises(ValidationError):
            self.service.send_voucher(
                voucher_id=voucher.id,
                recipient_email="someoneelse@example.com"
            )

    def test_apply_voucher_to_purchase_partial(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=100)

        result = self.service.apply_voucher_to_purchase(voucher_id=voucher.id, purchase_amount=40)
        self.assertEqual(result['amount_used'], 40)
        self.assertEqual(result['remaining'], 60)
        self.assertEqual(result['voucher'].status, 'active')

    def test_apply_voucher_to_purchase_full(self):
        voucher = self.service.purchase_voucher(user_id=self.user1.id, amount=50)

        result = self.service.apply_voucher_to_purchase(voucher_id=voucher.id, purchase_amount=60)
        self.assertEqual(result['amount_used'], 50)
        self.assertEqual(result['remaining'], 0)
        self.assertEqual(result['voucher'].status, 'used')

    def test_get_user_vouchers(self):
        Voucher.objects.all().delete()

        v1 = self.service.purchase_voucher(user_id=self.user1.id, amount=100)
        v2 = self.service.purchase_voucher(user_id=self.user1.id, amount=50)
        v3 = self.service.purchase_voucher(user_id=self.user1.id, amount=25)

        vouchers = self.service.get_user_vouchers(user_id=self.user1.id)
        self.assertEqual(len(vouchers), 3)
        for voucher in vouchers:
            self.assertEqual(voucher.owner, self.user1)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(VoucherServiceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
