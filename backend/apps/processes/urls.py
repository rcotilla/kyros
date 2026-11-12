"""URL configuration for processes app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcessTypeViewSet, ProcessViewSet

app_name = 'processes'

router = DefaultRouter()
router.register('process-types', ProcessTypeViewSet, basename='process-type')
router.register('processes', ProcessViewSet, basename='process')

urlpatterns = [
    path('', include(router.urls)),
]
