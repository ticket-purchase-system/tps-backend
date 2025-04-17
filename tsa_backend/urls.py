from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views.user_event_favorite import UserEventFavoriteViewSet
from app.views.user_views import UserViewSet
from app.views.event_views import EventViewSet

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'events', EventViewSet, basename='events')
router.register(r'events/favorites', UserEventFavoriteViewSet, basename='events/favorites')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
