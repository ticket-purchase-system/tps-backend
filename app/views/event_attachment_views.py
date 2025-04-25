from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from app.models import EventAttachment, EventDetails
from app.serializers.event_attachment_create_serializer import EventAttachmentCreateSerializer
from app.serializers.event_attachment_serializer import EventAttachmentSerializer


class EventAttachmentViewSet(viewsets.ModelViewSet):
    queryset = EventAttachment.objects.all()
    serializer_class = EventAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if self.request.user.is_staff:
            return EventAttachment.objects.all()
        return EventAttachment.objects.filter(event_details__event__organizer=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventAttachmentCreateSerializer
        return EventAttachmentSerializer

    def create(self, request, *args, **kwargs):
        # Extract event_details_id from the request
        event_details_id = request.data.get('event_details')
        event_details = get_object_or_404(EventDetails, id=event_details_id)

        # Check permissions
        event = event_details.event
        if not (request.user.is_staff or event.organizer == request.user):
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Associate with event_details
        serializer.save(event_details=event_details)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Endpoint to download attachment"""
        attachment = self.get_object()

        response = HttpResponse(attachment.file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{attachment.file.name.split("/")[-1]}"'
        return response

    @action(detail=False, methods=['get'])
    def by_event_details(self, request):
        """Get all attachments for a specific event details"""
        event_details_id = request.query_params.get('event_details')
        if not event_details_id:
            return Response(
                {"detail": "event_details parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        event_details = get_object_or_404(EventDetails, id=event_details_id)
        # Check permissions
        if not (request.user.is_staff or event_details.event.organizer == request.user):
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        attachments = EventAttachment.objects.filter(event_details=event_details)
        serializer = self.get_serializer(attachments, many=True)
        return Response(serializer.data)