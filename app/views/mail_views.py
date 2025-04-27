# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from app.models import Order


@api_view(['POST'])
def send_ticket_email(request, pk):
    order = get_object_or_404(Order, pk=pk)
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Brakuje adresu e-mail'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        send_mail(
            subject=f'Bilet dla zamówienia #{order.id}',
            message='Tu znajduje się Twój bilet.',
            from_email=None,
            recipient_list=[email],
        )
        return Response({'message': 'Email wysłany'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)