from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from app.views.user_views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
urlpatterns = [
    path('admin/', admin.site.urls),
]
