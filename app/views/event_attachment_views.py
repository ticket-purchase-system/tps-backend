from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from app.models import EventAttachment, EventDetails
from app.serializers.event_attachment_create_serializer import EventAttachmentCreateSerializer
from app.serializers.event_attachment_serializer import EventAttachmentSerializer
import os
import logging

logger = logging.getLogger(__name__)


class EventAttachmentViewSet(viewsets.ModelViewSet):
    queryset = EventAttachment.objects.all()
    serializer_class = EventAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return EventAttachment.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventAttachmentCreateSerializer
        return EventAttachmentSerializer

    def create(self, request, *args, **kwargs):
        try:
            logger.debug(f"Request data: {request.data}")

            event_details_id = request.data.get('event_details')

            if not event_details_id:
                return Response(
                    {"detail": "event_details parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            event_details = get_object_or_404(EventDetails, id=event_details_id)

            if 'file' not in request.data:
                return Response({"detail": "File is required"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            attachment = serializer.save(event_details=event_details)

            logger.debug(f"Attachment created successfully: {attachment.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            logger.error(f"Error in create: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Endpoint to download attachment"""
        try:
            attachment = self.get_object()

            if not attachment.file:
                return Response(
                    {"detail": "File not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if not os.path.exists(attachment.file.path):
                return Response(
                    {"detail": "File not found on disk"},
                    status=status.HTTP_404_NOT_FOUND
                )

            file_name = os.path.basename(attachment.file.name)

            response = FileResponse(
                open(attachment.file.path, 'rb'),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response

        except Exception as e:
            logger.error(f"Error downloading attachment: {str(e)}")
            return Response(
                {"detail": f"Error downloading file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

        event = event_details.event
        if not (request.user.is_staff or event.organizer == request.user):
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        attachments = EventAttachment.objects.filter(event_details=event_details)
        serializer = self.get_serializer(attachments, many=True)
        return Response(serializer.data)