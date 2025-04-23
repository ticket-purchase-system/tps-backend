from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from app.models import LoyaltyProgram, AppUser
from app.serializers.loyalty_program_serializer import LoyaltyProgramSerializer

class LoyaltyProgramViewSet(viewsets.ViewSet):
    """
    A viewset for managing loyalty program memberships.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all loyalty program members (admin only)"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            
            # Check if user is admin
            if app_user.role != 'admin':
                return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
                
            members = LoyaltyProgram.objects.all()
            serializer = LoyaltyProgramSerializer(members, many=True)
            return Response(serializer.data)
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Join the loyalty program"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            
            # Check if user is already in loyalty program
            if LoyaltyProgram.objects.filter(user=app_user).exists():
                return Response(
                    {"detail": "User is already a member of the loyalty program"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new loyalty program membership
            data = {
                'user': app_user.id,
                'preferences': request.data.get('preferences', {})
            }
            
            serializer = LoyaltyProgramSerializer(data=data)
            if serializer.is_valid():
                membership = serializer.save()
                return Response(
                    LoyaltyProgramSerializer(membership).data, 
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, pk=None):
        """Get user's loyalty program details"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            
            # If pk is "me", get the current user's loyalty program
            if pk == "me":
                try:
                    membership = LoyaltyProgram.objects.get(user=app_user)
                    serializer = LoyaltyProgramSerializer(membership)
                    return Response(serializer.data)
                except LoyaltyProgram.DoesNotExist:
                    return Response(
                        {"detail": "User is not a member of the loyalty program"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Only admins can view other users' loyalty programs
            if app_user.role != 'admin':
                return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
                
            membership = LoyaltyProgram.objects.get(id=pk)
            serializer = LoyaltyProgramSerializer(membership)
            return Response(serializer.data)
        except (AppUser.DoesNotExist, LoyaltyProgram.DoesNotExist):
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, pk=None):
        """Update loyalty program preferences"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            
            # If pk is "me", update the current user's loyalty program
            if pk == "me":
                try:
                    membership = LoyaltyProgram.objects.get(user=app_user)
                except LoyaltyProgram.DoesNotExist:
                    return Response(
                        {"detail": "User is not a member of the loyalty program"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Only admins can update other users' loyalty programs
                if app_user.role != 'admin':
                    return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
                
                membership = LoyaltyProgram.objects.get(id=pk)
            
            # Update preferences
            data = {
                'user': membership.user.id,
                'preferences': request.data.get('preferences', membership.preferences)
            }
            
            serializer = LoyaltyProgramSerializer(membership, data=data, partial=True)
            if serializer.is_valid():
                updated_membership = serializer.save()
                return Response(LoyaltyProgramSerializer(updated_membership).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (AppUser.DoesNotExist, LoyaltyProgram.DoesNotExist):
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def check_membership(self, request):
        """Check if current user is a loyalty program member"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            is_member = LoyaltyProgram.objects.filter(user=app_user).exists()
            
            return Response({
                "is_member": is_member
            })
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a loyalty program membership"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            
            # If pk is "me", deactivate the current user's membership
            if pk == "me":
                try:
                    membership = LoyaltyProgram.objects.get(user=app_user)
                except LoyaltyProgram.DoesNotExist:
                    return Response(
                        {"detail": "User is not a member of the loyalty program"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Only admins can deactivate other users' memberships
                if app_user.role != 'admin':
                    return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
                
                membership = LoyaltyProgram.objects.get(id=pk)
            
            membership.is_active = False
            membership.save()
            
            return Response(
                {"detail": "Loyalty program membership deactivated"}, 
                status=status.HTTP_200_OK
            )
        except (AppUser.DoesNotExist, LoyaltyProgram.DoesNotExist):
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND) 