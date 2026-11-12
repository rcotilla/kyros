"""URL configuration for clients app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet

app_name = 'clients'

router = DefaultRouter()
router.register('clients', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
