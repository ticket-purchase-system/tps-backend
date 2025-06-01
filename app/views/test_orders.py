from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import AppUser, Order, Product, Review, OrderProduct


class OrderViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.admin_user = User.objects.create_user(username='admin', password='adminpass')

        self.app_user = AppUser.objects.create(user=self.user, role='user')
        self.admin_app_user = AppUser.objects.create(user=self.admin_user, role='admin')

        self.product = Product.objects.create(description='Bilet', price=10.0)
        self.order = Order.objects.create(
            user=self.user,
            email='test@example.com',
            city='Warsaw',
            address='Main St',
            price=10.0,
            phoneNumber='987654321',
        )
        OrderProduct.objects.create(order=self.order, product=self.product)
        self.client = APIClient()

    def authenticate(self, admin=False):
        user = self.admin_user if admin else self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    def test_list_orders_admin_only(self):
        self.authenticate(admin=True)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.authenticate(admin=False)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_my_orders(self):
        user = User.objects.create_user(username='custom', password='pass')
        AppUser.objects.create(id=user.id, user=user, role='user', first_name='X', last_name='Y')

        Order.objects.create(user=user, email='x@example.com', city='City', address='Addr', price=99)

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        response = self.client.get('/api/orders/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_order_access_control(self):
        other_user = User.objects.create_user(username='other', password='123')
        AppUser.objects.create(user=other_user, role='user')
        other_order = Order.objects.create(user=other_user, email='o@example.com', city='Krk', address='Street', price=20.0)

        self.authenticate()
        response = self.client.get(f'/api/orders/{other_order.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_download_pdf(self):
        self.authenticate()
        response = self.client.get(f'/api/orders/{self.order.id}/download-pdf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_add_review_success(self):
        self.authenticate()
        payload = {'numberOfStars': '5', 'comment': 'Great!', 'rating': 5}
        response = self.client.post(f'/api/orders/{self.order.id}/add_review/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_review_already_exists(self):
        self.authenticate()
        review = Review.objects.create(numberOfStars='4', comment='Old', rating=4)
        self.order.review = review
        self.order.save()

        payload = {'numberOfStars': '5', 'comment': 'New', 'rating': 5}
        response = self.client.post(f'/api/orders/{self.order.id}/add_review/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_review(self):
        self.authenticate()
        review = Review.objects.create(numberOfStars='4', comment='Old', rating=4)
        self.order.review = review
        self.order.save()

        response = self.client.delete(f'/api/orders/{self.order.id}/delete_review/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.order.refresh_from_db()
        self.assertIsNone(self.order.review)

    def test_create_order(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        AppUser.objects.create(id=user.id, user=user, role='user', first_name='Test', last_name='User')

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        data = {
            'email': 'create@example.com',
            'city': 'City',
            'address': 'Address',
            'price': 25.0,
            'phoneNumber': '123456789',
            'products': [{'id': self.product.id}]
        }

        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_order(self):
        user = User.objects.create_user(username='retrieveuser', password='testpass')
        AppUser.objects.create(id=user.id, user=user, role='user', first_name='Test', last_name='Retrieve')

        order = Order.objects.create(
            user=user,
            email='test@example.com',
            city='Warsaw',
            address='Main St',
            phoneNumber='987654321',
            price=10.0
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        response = self.client.get(f'/api/orders/{order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order(self):
        user = User.objects.create_user(username='updateuser', password='testpass')
        AppUser.objects.create(id=user.id, user=user, role='user', first_name='Test', last_name='Update')

        order = Order.objects.create(
            user=user,
            email='update@example.com',
            city='Old City',
            address='Update St',
            phoneNumber='000000000',
            price=99.0
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        data = {'city': 'Updated City'}
        response = self.client.put(f'/api/orders/{order.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'Updated City')

    def test_delete_order(self):
        user = User.objects.create_user(username='deleteuser', password='testpass')
        AppUser.objects.create(id=user.id, user=user, role='user', first_name='Test', last_name='Delete')

        order = Order.objects.create(
            user=user,
            email='delete@example.com',
            city='Delete City',
            address='Del St',
            phoneNumber='999999999',
            price=50.0
        )

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        response = self.client.delete(f'/api/orders/{order.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_orders_by_admin(self):
        self.authenticate(admin=True)
        response = self.client.get(f'/api/orders/user/{self.app_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_orders_by_self(self):
        self.authenticate()
        response = self.client.get(f'/api/orders/user/{self.app_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_orders_unauthorized(self):
        other_user = User.objects.create_user(username='other', password='pass')
        other_app_user = AppUser.objects.create(user=other_user, role='user')

        self.authenticate()
        response = self.client.get(f'/api/orders/user/{other_app_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review(self):
        self.authenticate()
        review = Review.objects.create(numberOfStars='4', comment='Old', rating=4)
        self.order.review = review
        self.order.save()

        data = {'comment': 'Updated'}
        response = self.client.put(f'/api/orders/{self.order.id}/update_review/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'Updated')

    def test_update_review_none(self):
        self.authenticate()
        response = self.client.put(f'/api/orders/{self.order.id}/update_review/', {'comment': 'Attempt'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_has_issue_false(self):
        self.authenticate()
        response = self.client.get(f'/api/orders/{self.order.id}/has-issue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['hasIssue'])

    def test_has_refund_false(self):
        self.authenticate()
        response = self.client.get(f'/api/orders/{self.order.id}/has-refund/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['hasRefund'])

