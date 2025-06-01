from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Product, Review, Order, OrderProduct, IssueReport, RefundRequest


class OrdersTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.product = Product.objects.create(price=10.0, description='Test product')
        self.review = Review.objects.create(
            numberOfStars='5',
            comment='Excellent',
            rating=5
        )
        self.order = Order.objects.create(
            user=self.user,
            email='test@example.com',
            city='City',
            address='123 Main St',
            phoneNumber='123456789',
            price=20.0,
            review=self.review
        )
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )
        self.issue = IssueReport.objects.create(order=self.order, opis='Problem')
        self.refund = RefundRequest.objects.create(order=self.order, reason='Did not arrive')

    def test_product_str(self):
        self.assertIn('Product', str(self.product))

    def test_review_str(self):
        self.assertIn('Review', str(self.review))
        self.assertEqual(self.review.numberOfStars, '5')

    def test_order_str(self):
        self.assertIn('Order', str(self.order))
        self.assertEqual(self.order.products.count(), 1)

    def test_order_product_str(self):
        self.assertIn(str(self.product.id), str(self.order_product))
        self.assertEqual(self.order_product.quantity, 2)

    def test_issue_report(self):
        self.assertEqual(self.issue.status, 'NEW')
        self.assertIn('IssueReport', str(self.issue))

    def test_refund_request(self):
        self.assertEqual(self.refund.status, 'NEW')
        self.assertIn('RefundRequest', str(self.refund))
