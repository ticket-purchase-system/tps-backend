from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

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
        app_user = get_object_or_404(AppUser, user=request.user)
        data = request.data.copy()
        data['user'] = app_user.id
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

    @action(detail=False, methods=['get'])
    def me(self, request):
        """GET /orders/me/ — lista zamówień zalogowanego użytkownika"""
        app_user = get_object_or_404(AppUser, user=request.user)
        orders = Order.objects.filter(user_id=app_user.id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

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