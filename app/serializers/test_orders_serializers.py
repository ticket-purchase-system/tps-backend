from django.test import TestCase
from django.contrib.auth.models import User
from app.models import (
    Product, Review, Order, OrderProduct, IssueReport, RefundRequest
)
from app.serializers.orders_serializer import ProductSerializer, ReviewSerializer, OrderSerializer, \
    IssueReportSerializer, RefundRequestSerializer


class SerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.product = Product.objects.create(description='Test product', price=123.45)
        self.review = Review.objects.create(
            numberOfStars='5', comment='Excellent!', rating=10
        )
        self.order = Order.objects.create(
            user=self.user,
            email='test@example.com',
            city='Warsaw',
            address='Main St',
            phoneNumber='123456789',
            price=123.45,
            review=self.review
        )
        OrderProduct.objects.create(order=self.order, product=self.product, quantity=2)
        self.issue_report = IssueReport.objects.create(order=self.order, opis='Problem...')
        self.refund_request = RefundRequest.objects.create(order=self.order, reason='Item broken')

    def test_product_serializer(self):
        serializer = ProductSerializer(instance=self.product)
        self.assertEqual(serializer.data['description'], 'Test product')

    def test_review_serializer(self):
        serializer = ReviewSerializer(instance=self.review)
        self.assertEqual(serializer.data['numberOfStars'], '5')

    def test_order_serializer_output(self):
        serializer = OrderSerializer(instance=self.order)
        self.assertEqual(serializer.data['user'], self.user.id)
        self.assertEqual(serializer.data['review']['comment'], 'Excellent!')

    def test_order_serializer_create(self):
        data = {
            'user': self.user.id,
            'price': 50.0,
            'email': 'test@example.com',
            'city': 'Warsaw',
            'address': 'Street',
            'phoneNumber': '987654321',
            'products': [{'id': self.product.id}]
        }
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(order.products.count(), 1)
        self.assertEqual(OrderProduct.objects.filter(order=order).count(), 1)

    def test_issue_report_serializer(self):
        serializer = IssueReportSerializer(instance=self.issue_report)
        self.assertEqual(serializer.data['status'], 'NEW')
        self.assertEqual(serializer.data['opis'], 'Problem...')

    def test_refund_request_serializer(self):
        serializer = RefundRequestSerializer(instance=self.refund_request)
        self.assertEqual(serializer.data['status'], 'NEW')
        self.assertEqual(serializer.data['reason'], 'Item broken')

    def test_invalid_order_missing_fields(self):
        serializer = OrderSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)

    def test_issue_report_read_only_fields(self):
        data = {'opis': 'Coś', 'status': 'RESOLVED'}
        serializer = IssueReportSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        saved = serializer.save(order=self.order)
        self.assertEqual(saved.status, 'NEW')
