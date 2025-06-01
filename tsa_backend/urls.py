from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views.artist_views import ArtistViewSet
from app.views.orders_views import OrderViewSet, ProductViewSet, TicketsViewSet, ReviewViewSet, OrderIssueViewSet, \
    OrderRefundViewSet
from app.views.event_attachment_views import EventAttachmentViewSet
from app.views.event_details_views import EventDetailsViewSet
from app.views.user_event_favorite import UserEventFavoriteViewSet
from app.views.user_views import UserViewSet
from app.views.event_views import EventViewSet
from app.views.technical_issue_views import TechnicalIssueViewSet
from app.views.loyalty_program_views import LoyaltyProgramViewSet
from app.views.ticket_view import BasketView
from app.views.voucher_views import VoucherViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from app.views.mail_views import send_ticket_email
from django.conf import settings
from django.conf.urls.static import static
from app.views.statistics_views import (
    event_statistics,
    top_selling_events,
    monthly_trends,
    event_type_distribution,
    toggle_data_source,
    data_source_status
)

router = DefaultRouter()

# Remove the users registration from router since we're handling it manually
# router.register(r'users', UserViewSet, basename='users')
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
router.register(r'vouchers', VoucherViewSet, basename='vouchers')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/events/statistics/', event_statistics, name='event-statistics'),
    path('api/events/statistics/top-selling/', top_selling_events, name='top-selling-events'),
    path('api/events/statistics/monthly-trends/', monthly_trends, name='monthly-trends'),
    path('api/events/statistics/type-distribution/', event_type_distribution, name='event-type-distribution'),
    path('api/events/statistics/toggle-data-source/', toggle_data_source, name='toggle-data-source'),
    path('api/events/statistics/data-source-status/', data_source_status, name='data-source-status'),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # User endpoints
    path('api/users/', UserViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('api/users/reset-password/', UserViewSet.as_view({
        'post': 'reset_password'
    })),
    path('api/users/<str:pk>/', UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),

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
    path('api/basket/<int:pk>', BasketView.as_view()),
    # Voucher endpoints
    path('api/vouchers/user', VoucherViewSet.as_view({'get': 'user'})),
    path('api/vouchers/purchase', VoucherViewSet.as_view({'post': 'purchase'})),
    path('api/vouchers/validate/<str:code>', VoucherViewSet.as_view({'get': 'validate'})),
    path('api/vouchers/redeem', VoucherViewSet.as_view({'post': 'redeem'})),
    path('api/vouchers/<int:id>/send', VoucherViewSet.as_view({'post': 'send'})),
    path('api/vouchers/apply', VoucherViewSet.as_view({'post': 'apply'})),

    path('api/orders', OrderViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/orders/<pk>', OrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/orders/user/<user_id>', OrderViewSet.as_view({'get': 'user_orders'})),

    path('api/orders/<int:pk>/send-email/', send_ticket_email),
    path('api/events/favorites/user/<int:user_id>/', UserEventFavoriteViewSet.as_view({'get': 'user_favorites'})),
    path('api/orders/<int:pk>/add_review/', OrderViewSet.as_view({'post': 'add_review'})),
    path('api/orders/<int:pk>/update_review/', OrderViewSet.as_view({'put': 'update_review'})),
    path('api/orders/<int:pk>/delete_review/', OrderViewSet.as_view({'delete': 'delete_review'})),
    path('api/orders/<int:pk>/add-product/', OrderViewSet.as_view({'post': 'add_product'})),


    path(
        'api/orders/<int:pk>/has-issue/',
        OrderIssueViewSet.as_view({'get': 'has_issue'}),
        name='order-has-issue'
    ),
    path(
        'api/orders/<int:pk>/report-issue/',
        OrderIssueViewSet.as_view({'post': 'report_issue'}),
        name='order-report-issue'
    ),
    path(
        'api/orders/<int:pk>/has-refund/',
        OrderRefundViewSet.as_view({'get': 'has_refund'}),
        name='order-has-refund'
    ),
    path(
        'api/orders/<int:pk>/refund/',
        OrderRefundViewSet.as_view({'post': 'create_refund'}),
        name='order-refund'
    ),

    path('api/orders/<int:pk>/download-pdf/', OrderViewSet.as_view({'get': 'download_pdf'})),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)