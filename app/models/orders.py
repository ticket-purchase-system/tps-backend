from django.db import models
from django.utils import timezone
from django.conf import settings

class Opinion(models.TextChoices):
    ONE_STAR = '1'
    TWO_STARS = '2'
    THREE_STARS = '3'
    FOUR_STARS = '4'
    FIVE_STARS = '5'

class Product(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"Product {self.id}: {self.description[:20]}"

    class Meta:
        abstract = False

# class Tickets(Product):
#     sector = models.CharField(max_length=50)
#     seat = models.IntegerField(null=True, blank=True)
#
#     def __str__(self):
#         seat_info = f", seat {self.seat}" if self.seat is not None else ""
#         return f"Ticket {self.id} ({self.sector}{seat_info})"

class Review(models.Model):
    numberOfStars = models.CharField(
        max_length=1,
        choices=Opinion.choices,
        default=Opinion.FIVE_STARS,
        db_column='numberOfStars'
    )
    comment = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField()

    def __str__(self):
        return f"Review {self.id}: {self.numberOfStars} stars"

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    date = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rabatCode = models.CharField(max_length=50, blank=True, null=True)
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True, blank=True)
    phoneNumber = models.CharField(max_length=20)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    address = models.TextField()
    products = models.ManyToManyField(Product, through='OrderProduct')

    def __str__(self):
        return f"Order {self.id} by {self.user} on {self.date:%Y-%m-%d}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product} (Order {self.order.id})"



class IssueReport(models.Model):
    """
    Zgłoszenie problemu dla zamówienia
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='issue_reports'
    )
    opis = models.TextField()
    zalacznik = models.FileField(upload_to='issue_attachments/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('NEW', 'Nowe'),
            ('IN_PROGRESS', 'W trakcie'),
            ('RESOLVED', 'Rozwiązane'),
        ],
        default='NEW'
    )
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"IssueReport {self.id} ({self.status}) for Order {self.order.id}"


class RefundStatus(models.TextChoices):
    NEW       = 'NEW',       'Nowy'
    APPROVED  = 'APPROVED',  'Zaakceptowany'
    REJECTED  = 'REJECTED',  'Odrzucony'

class RefundRequest(models.Model):
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='refund_requests'
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.NEW
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"RefundRequest #{self.id} ({self.status}) for Order {self.order_id}"