from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from app.models import EventDetails, EventAttachment, Event
from app.serializers.event_details_serializer import EventDetailsSerializer

class EventDetailsViewSet(viewsets.ModelViewSet):
    queryset = EventDetails.objects.all()
    serializer_class = EventDetailsSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if self.request.user.is_staff:
            return EventDetails.objects.all()
        return EventDetails.objects.filter(event__organizer=self.request.user)

    def create(self, request, *args, **kwargs):
        # Get event ID from request data
        event_id = request.data.get('event')
        event = get_object_or_404(Event, id=event_id)

        # Check if event details already exist
        event_details, created = EventDetails.objects.get_or_create(event=event)

        if not created:
            return Response(
                {"detail": "Event details already exist. Use PUT or PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use the existing object for serialization
        serializer = self.get_serializer(event_details, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download_rules(self, request, pk=None):
        """Endpoint to download rules PDF"""
        event_details = self.get_object()

        if not event_details.rules_pdf:
            return Response(
                {"detail": "No rules PDF available"},
                status=status.HTTP_404_NOT_FOUND
            )

        response = HttpResponse(event_details.rules_pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{event_details.event.title}_rules.pdf"'
        return response

    @action(detail=True, methods=['get'])
    def by_event(self, request, pk=None):
        """Get event details by event ID"""
        event = get_object_or_404(Event, id=pk)
        event_details, created = EventDetails.objects.get_or_create(event=event)
        serializer = self.get_serializer(event_details)
        return Response(serializer.data)


