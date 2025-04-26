import os

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import logging
from app.models import EventDetails, EventAttachment, Event
from app.serializers.event_details_serializer import EventDetailsSerializer
from tsa_backend import settings

logger = logging.getLogger(__name__)


class EventDetailsViewSet(viewsets.ModelViewSet):
    queryset = EventDetails.objects.all()
    serializer_class = EventDetailsSerializer
    # Add FileUploadParser to handle raw file uploads
    parser_classes = [MultiPartParser, FormParser, JSONParser, FileUploadParser]

    def get_queryset(self):
        return EventDetails.objects.all()

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

    def update(self, request, *args, **kwargs):
        """Override update to properly handle file uploads"""
        instance = self.get_object()

        # Debug information
        print(f"Update request content type: {request.content_type}")
        print(f"Request data keys: {request.data.keys() if hasattr(request.data, 'keys') else 'Not a dict'}")

        # Handle partial updates correctly
        partial = kwargs.pop('partial', False)

        # Check if this is a multipart request
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle multipart form data
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
        else:
            # For JSON or other content types
            serializer = self.get_serializer(instance, data=request.data, partial=partial)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests with files"""
        logger.info(f"PATCH request content type: {request.content_type}")
        logger.info(f"PATCH data: {request.data if hasattr(request.data, 'dict') else 'Not a dict'}")

        # Special handling for file uploads via PATCH
        if request.content_type and 'multipart/form-data' in request.content_type:
            instance = self.get_object()

            # Process each field in the form data
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # For regular PATCH requests
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def download_rules(self, request, pk=None):
        """Endpoint to download rules PDF"""
        try:
            event_details = self.get_object()

            if not event_details.rules_pdf:
                return Response(
                    {"detail": "No rules PDF available"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Debug information - print important paths
            print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
            print(f"PDF relative path: {event_details.rules_pdf.name}")

            # Try to access the file using absolute paths
            file_path = os.path.join(settings.MEDIA_ROOT, event_details.rules_pdf.name)
            print(f"Full file path: {file_path}")

            if not os.path.exists(file_path):
                print(f"File does not exist at: {file_path}")

                # Try alternate path (in case upload_to is causing issues)
                alt_path = os.path.join(settings.BASE_DIR, 'app', 'event_rules',
                                        os.path.basename(event_details.rules_pdf.name))
                print(f"Trying alternate path: {alt_path}")

                if os.path.exists(alt_path):
                    file_path = alt_path
                    print(f"Found file at alternate path: {alt_path}")
                else:
                    print(f"File not found at alternate path either: {alt_path}")
                    return Response(
                        {"detail": "PDF file not found on disk"},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Open file using standard Python file operations
            try:
                with open(file_path, 'rb') as pdf_file:
                    file_content = pdf_file.read()

                response = HttpResponse(file_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{event_details.event.title}_rules.pdf"'
                return response
            except Exception as file_error:
                print(f"Error reading file: {file_error}")
                return Response(
                    {"detail": f"Error reading file: {str(file_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            import traceback
            print(f"Error in download_rules: {e}")
            print(traceback.format_exc())
            return Response(
                {"detail": f"Error downloading PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def by_event(self, request, pk=None):
        """Get event details by event ID"""
        event = get_object_or_404(Event, id=pk)
        event_details, created = EventDetails.objects.get_or_create(event=event)
        serializer = self.get_serializer(event_details)
        return Response(serializer.data)

    # Add a dedicated endpoint for updating the PDF file only
    @action(detail=True, methods=['post'], url_path='update-rules')
    def update_rules(self, request, pk=None):
        """Dedicated endpoint for updating just the rules PDF"""
        event_details = self.get_object()

        if 'rules_pdf' not in request.FILES:
            return Response(
                {"detail": "No rules PDF file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update just the PDF file
        event_details.rules_pdf = request.FILES['rules_pdf']
        event_details.save()

        serializer = self.get_serializer(event_details)
        return Response(serializer.data)