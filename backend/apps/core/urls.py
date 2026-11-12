"""
URL configuration for core app.

API endpoints for:
- User authentication and profiles
- Role information
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserProfileViewSet, RoleViewSet, AuthStatusView

app_name = 'core'

router = DefaultRouter()
router.register('user', UserProfileViewSet, basename='user')
router.register('roles', RoleViewSet, basename='role')
router.register('auth', AuthStatusView, basename='auth')

urlpatterns = [
    # API v1 routes
    path('', include(router.urls)),

    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Django REST Framework browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]
