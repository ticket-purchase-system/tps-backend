from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from app.views.orders_views import generate_order_pdf
from app.models import Order


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_ticket_email(request, pk):
    order = get_object_or_404(Order, pk=pk)
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Brakuje adresu e-mail'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pdf_buffer = generate_order_pdf(order)

        message = EmailMessage(
            subject=f"Bilet dla zamówienia #{order.id}",
            body="W załączniku znajdziesz swój bilet w formacie PDF.",
            from_email=None,
            to=[email]
        )
        message.attach(f"bilet_zamowienie_{order.id}.pdf", pdf_buffer.read(), "application/pdf")
        message.send()

        return Response({'message': 'Email z załącznikiem został wysłany'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)