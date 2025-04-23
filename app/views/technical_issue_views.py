from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.models import TechnicalIssue, AppUser
from app.serializers.technical_issue_serializer import TechnicalIssueSerializer

class TechnicalIssueViewSet(viewsets.ViewSet):
    """
    A viewset for managing technical issue reports.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all technical issues for the authenticated user"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            issues = TechnicalIssue.objects.filter(user=app_user)
            serializer = TechnicalIssueSerializer(issues, many=True)
            return Response(serializer.data)
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Create a new technical issue report"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            data = request.data.copy()
            data['user'] = app_user.id
            
            serializer = TechnicalIssueSerializer(data=data)
            if serializer.is_valid():
                issue = serializer.save()
                return Response(TechnicalIssueSerializer(issue).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, pk=None):
        """Retrieve a specific technical issue"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            issue = TechnicalIssue.objects.get(id=pk, user=app_user)
            serializer = TechnicalIssueSerializer(issue)
            return Response(serializer.data)
        except (AppUser.DoesNotExist, TechnicalIssue.DoesNotExist):
            return Response({"detail": "Issue not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, pk=None):
        """Update an existing technical issue (only title, description, priority)"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            issue = TechnicalIssue.objects.get(id=pk, user=app_user)
            
            # Only allow updating specific fields
            data = {
                'user': app_user.id,
                'title': request.data.get('title', issue.title),
                'description': request.data.get('description', issue.description),
                'priority': request.data.get('priority', issue.priority)
            }
            
            serializer = TechnicalIssueSerializer(issue, data=data, partial=True)
            if serializer.is_valid():
                updated_issue = serializer.save()
                return Response(TechnicalIssueSerializer(updated_issue).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (AppUser.DoesNotExist, TechnicalIssue.DoesNotExist):
            return Response({"detail": "Issue not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, pk=None):
        """Delete a technical issue"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            issue = TechnicalIssue.objects.get(id=pk, user=app_user)
            issue.delete()
            return Response({"detail": "Issue deleted"}, status=status.HTTP_204_NO_CONTENT)
        except (AppUser.DoesNotExist, TechnicalIssue.DoesNotExist):
            return Response({"detail": "Issue not found"}, status=status.HTTP_404_NOT_FOUND) 