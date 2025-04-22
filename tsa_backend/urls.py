from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views.user_event_favorite import UserEventFavoriteViewSet
from app.views.user_views import UserViewSet
from app.views.event_views import EventViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'events', EventViewSet, basename='events')
router.register(r'events/favorites', UserEventFavoriteViewSet, basename='events/favorites')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/users', UserViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/users/<pk>', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # login - get access and refresh tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # refresh - get new access token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # logout - when refresh token expires
    path('api/token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
