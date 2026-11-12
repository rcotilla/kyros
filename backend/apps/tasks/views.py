"""Views for tasks app."""

from rest_framework import viewsets, permissions, filters
from django.db import models
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """API endpoint for tasks."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return tasks assigned to user or created by user."""
        user = self.request.user
        return Task.objects.filter(
            models.Q(assigned_to=user) | models.Q(created_by=user)
        ).distinct()

    def perform_create(self, serializer):
        """Force created_by to the current user to prevent forgery."""
        serializer.save(created_by=self.request.user)
