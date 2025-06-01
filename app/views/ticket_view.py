from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.serializers.ticket_serializer import TicketSerializer
from app.services.ticket_service import TicketService
from rest_framework import status
from django.shortcuts import get_object_or_404
from app.models import Ticket
import traceback

class BasketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            tickets = TicketService.get_user_basket(request.user)
            serializer = TicketSerializer(tickets, many=True)

            return Response(serializer.data)
        except Exception as e:
            print("BASKET GET ERROR:", e)
            return Response({"error": str(e)}, status=500)

    def post(self, request):
        print("DANE Z REQUESTU:", request.data)
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            print("SERIALIZER OK, dodajemy do koszyka")
            ticket = serializer.save(user=request.user)
            return Response(TicketSerializer(ticket).data)

        print("SERIALIZER ERRORS:", serializer.errors)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk, user=request.user)
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
