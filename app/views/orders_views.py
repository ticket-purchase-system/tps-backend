from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import logging
from app.models.orders import OrderProduct


from app.models import AppUser
from app.models.orders import Order, Product, Tickets, Review
from app.serializers.orders_serializer import (
    OrderSerializer,
    ProductSerializer,
    TicketsSerializer,
    ReviewSerializer
)


class OrderViewSet(viewsets.ViewSet):
    """
    Zarządzanie zamówieniami:
     - admin może pobrać wszystkie zamówienia
     - użytkownicy mogą zarządzać tylko swoimi zamówieniami
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        app_user = get_object_or_404(AppUser, user=request.user)
        if app_user.role != 'admin':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger = logging.getLogger(__name__)
        logger.debug(f"Received order payload: {request.data}")
        app_user = get_object_or_404(AppUser, user=request.user)
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        app_user = get_object_or_404(AppUser, user=request.user)
        order = get_object_or_404(Order, pk=pk)
        if order.user_id != app_user.id and app_user.role != 'admin':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def update(self, request, pk=None):
        app_user = get_object_or_404(AppUser, user=request.user)
        order = get_object_or_404(Order, pk=pk)
        if order.user_id != app_user.id and app_user.role != 'admin':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['user'] = order.user_id
        serializer = OrderSerializer(order, data=data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(OrderSerializer(updated).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        app_user = get_object_or_404(AppUser, user=request.user)
        order = get_object_or_404(Order, pk=pk)
        if order.user_id != app_user.id and app_user.role != 'admin':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_orders(self, request, user_id=None):
        """GET /orders/user/{user_id}/ — lista zamówień wskazanego użytkownika"""
        app_user = get_object_or_404(AppUser, user=request.user)
        if app_user.role != 'admin' and str(app_user.id) != str(user_id):
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        target_app_user = get_object_or_404(AppUser, pk=user_id)
        orders = Order.objects.filter(user=target_app_user.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='add-product')
    def add_product(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        product = get_object_or_404(Product, pk=product_id)
        order_product = OrderProduct.objects.create(order=order, product=product, quantity=quantity)

        return Response({
            "message": "Product added to order",
            "order_id": order.id,
            "product_id": product.id,
            "quantity": quantity
        }, status=201)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """GET /orders/me/ — lista zamówień zalogowanego użytkownika"""
        app_user = get_object_or_404(AppUser, user=request.user)
        orders = Order.objects.filter(user_id=app_user.id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        """POST /orders/{pk}/add_review/ — dodaj recenzję do zamówienia"""
        try:
            app_user = get_object_or_404(AppUser, user=request.user)
            order = get_object_or_404(Order, pk=pk)

            if order.user_id != app_user.user.id:
                return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

            if order.review is not None:
                return Response({"detail": "Order already has a review"}, status=status.HTTP_400_BAD_REQUEST)

            review_data = request.data.copy()

            review_serializer = ReviewSerializer(data=review_data)

            if review_serializer.is_valid():
                review = review_serializer.save()

                order.review = review
                order.save()

                return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
            else:
                print(review_serializer.errors)
                return Response(review_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error adding review: {str(e)}")
            return Response({"detail": f"An error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['put'])
    def update_review(self, request, pk=None):
        """PUT /orders/{pk}/update_review/ — aktualizuj recenzję zamówienia"""
        app_user = get_object_or_404(AppUser, user=request.user)
        order = get_object_or_404(Order, pk=pk)

        if order.user_id != app_user.id and app_user.role != 'admin':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        if order.review is None:
            return Response({"detail": "Order has no review to update"}, status=status.HTTP_400_BAD_REQUEST)

        review_data = request.data
        review_serializer = ReviewSerializer(order.review, data=review_data, partial=True)

        if review_serializer.is_valid():
            review = review_serializer.save()
            return Response(ReviewSerializer(review).data)

        return Response(review_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_review(self, request, pk=None):
        """DELETE /orders/{pk}/delete_review/ — usuń recenzję zamówienia"""
        app_user = get_object_or_404(AppUser, user=request.user)
        order = get_object_or_404(Order, pk=pk)

        if order.user_id != app_user.id and app_user.role != 'admin':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        if order.review is None:
            return Response({"detail": "Order has no review to delete"}, status=status.HTTP_400_BAD_REQUEST)

        review = order.review
        order.review = None
        order.save()
        review.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD dla produktów"""
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class TicketsViewSet(viewsets.ModelViewSet):
    """CRUD dla biletów"""
    permission_classes = [IsAuthenticated]
    queryset = Tickets.objects.all()
    serializer_class = TicketsSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """CRUD dla recenzji"""
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    @action(detail=False, methods=['get'])
    def product_reviews(self, request):
        """GET /reviews/product_reviews/?product_id={id} — Get reviews for a specific product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({"detail": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, pk=product_id)
        reviews = Review.objects.filter(order__product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """GET /reviews/recent/?count={count} — Get recent reviews"""
        count = request.query_params.get('count', 5)
        try:
            count = int(count)
        except ValueError:
            count = 5

        reviews = Review.objects.all().order_by('-created_at')[:count]
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)