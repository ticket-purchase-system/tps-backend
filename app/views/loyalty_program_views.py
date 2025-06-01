from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from app.models import LoyaltyProgram, AppUser
from app.serializers.loyalty_program_serializer import LoyaltyProgramSerializer
from decimal import Decimal

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
            
            # Check if user has an active loyalty program membership
            active_membership = LoyaltyProgram.objects.filter(user=app_user, is_active=True).first()
            if active_membership:
                return Response(
                    {"detail": "User is already a member of the loyalty program"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user has an inactive membership that can be reactivated
            inactive_membership = LoyaltyProgram.objects.filter(user=app_user, is_active=False).first()
            if inactive_membership:
                # Reactivate the existing membership with fresh start - reset points and tier
                inactive_membership.is_active = True
                inactive_membership.preferences = request.data.get('preferences', {})
                inactive_membership.points = 0  # Reset points to 0
                inactive_membership.tier = 'bronze'  # Reset to bronze tier
                inactive_membership.save()
                return Response(
                    LoyaltyProgramSerializer(inactive_membership).data, 
                    status=status.HTTP_200_OK
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
                    # Only return active memberships
                    membership = LoyaltyProgram.objects.get(user=app_user, is_active=True)
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
            # Only consider active memberships
            is_member = LoyaltyProgram.objects.filter(user=app_user, is_active=True).exists()
            
            return Response({
                "is_member": is_member
            })
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def award_points(self, request):
        """Award points to a user for a purchase"""
        try:
            app_user = AppUser.objects.get(user=request.user)
            
            # Get or create loyalty program membership
            membership, created = LoyaltyProgram.objects.get_or_create(
                user=app_user,
                defaults={
                    'points': 0,
                    'tier': 'bronze',
                    'is_active': True,
                    'preferences': {}
                }
            )
            
            # Get purchase amount from request
            purchase_amount = Decimal(str(request.data.get('amount', 0)))
            
            # Calculate points: 10 points per $1 spent
            points_to_award = int(purchase_amount * 10)
            
            # Award the points
            old_points = membership.points
            membership.points += points_to_award
            
            # Check for tier advancement
            old_tier = membership.tier
            new_tier = self._calculate_tier(membership.points)
            membership.tier = new_tier
            
            membership.save()
            
            tier_advanced = old_tier != new_tier
            
            return Response({
                'points_awarded': points_to_award,
                'total_points': membership.points,
                'old_tier': old_tier,
                'new_tier': new_tier,
                'tier_advanced': tier_advanced,
                'membership': LoyaltyProgramSerializer(membership).data
            }, status=status.HTTP_200_OK)
            
        except AppUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_tier(self, points):
        """Calculate tier based on points"""
        if points >= 1000:
            return 'platinum'
        elif points >= 500:
            return 'gold'
        elif points >= 200:
            return 'silver'
        else:
            return 'bronze'
    
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