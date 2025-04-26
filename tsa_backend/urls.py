from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views.artist_views import ArtistViewSet
from app.views.orders_views import OrderViewSet, ProductViewSet, TicketsViewSet, ReviewViewSet
from app.views.event_attachment_views import EventAttachmentViewSet
from app.views.event_details_views import EventDetailsViewSet
from app.views.user_event_favorite import UserEventFavoriteViewSet
from app.views.user_views import UserViewSet
from app.views.event_views import EventViewSet
from app.views.technical_issue_views import TechnicalIssueViewSet
from app.views.loyalty_program_views import LoyaltyProgramViewSet
from app.views.ticket_view import BasketView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from app.views.mail_views import send_ticket_email
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'events', EventViewSet, basename='events')
router.register(r'events/favorites', UserEventFavoriteViewSet, basename='events/favorites')
router.register(r'technical-issues', TechnicalIssueViewSet, basename='technical-issues')
router.register(r'loyalty-program', LoyaltyProgramViewSet, basename='loyalty-program')
router.register(r'artists', ArtistViewSet, basename='artists')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'tickets', TicketsViewSet, basename='tickets')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'attachments', EventAttachmentViewSet, basename='attachments')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/users', UserViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/users/<pk>', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/technical-issues', TechnicalIssueViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/technical-issues/<pk>', TechnicalIssueViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    # Loyalty program endpoints - Make sure "check" endpoint is registered before the detail view
    path('api/loyalty-program/check', LoyaltyProgramViewSet.as_view({'get': 'check_membership'})),
    path('api/loyalty-program', LoyaltyProgramViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/loyalty-program/<pk>', LoyaltyProgramViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
    path('api/loyalty-program/<pk>/deactivate', LoyaltyProgramViewSet.as_view({'post': 'deactivate'})),

    path('api/events/<int:pk>/details/', EventDetailsViewSet.as_view({'get': 'by_event'}),
         name='event-details-by-event'),
    path('api/event-details/<int:pk>/download-rules/', EventDetailsViewSet.as_view({'get': 'download_rules'}),
         name='download-rules'),
    path('api/event-details/<int:pk>/', EventDetailsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    }), name='event-details'),
    path('api/attachments/<int:pk>/download', EventAttachmentViewSet.as_view({'get': 'download'}),
         name='download-attachment'),
    path('api/basket', BasketView.as_view()),
    path('api/basket/add', BasketView.as_view()),

    # login - get access and refresh tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # refresh - get new access token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # logout - when refresh token expires
    path('api/token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('api/orders', OrderViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/orders/<pk>', OrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/orders/user/<user_id>', OrderViewSet.as_view({'get': 'user_orders'})),

    path('api/orders/<int:pk>/send-email/', send_ticket_email),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)