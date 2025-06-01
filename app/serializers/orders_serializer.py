from django.contrib.auth import get_user_model
from rest_framework import serializers
from app.models.orders import Product, Review, OrderProduct, Order, IssueReport, RefundRequest

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'price', 'description', 'event']

# class TicketsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tickets
#         fields = ['id', 'price', 'description', 'sector', 'seat']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'numberOfStars', 'comment', 'date', 'rating']

class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    products = ProductSerializer(many=True, read_only=True)
    review = ReviewSerializer(read_only=True)
    order_products = OrderProductSerializer(source='orderproduct_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'date', 'price', 'rabatCode', 'review',
            'phoneNumber', 'email', 'city', 'address',
            'products', 'order_products'
        ]

    def create(self, validated_data):
        products_data = self.initial_data.get('products', [])
        order = Order.objects.create(**validated_data)

        for product_data in products_data:
            try:
                product = Product.objects.get(id=product_data.get('id'))
                OrderProduct.objects.create(order=order, product=product)
            except Product.DoesNotExist:
                continue

        return order


class IssueReportSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = IssueReport
        fields = ['id', 'order', 'opis', 'zalacznik', 'status', 'data']
        read_only_fields = ['id', 'order', 'status', 'data']

class RefundRequestSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RefundRequest
        fields = ['id', 'order', 'reason', 'status', 'date']
        read_only_fields = ['id', 'order', 'status', 'date']