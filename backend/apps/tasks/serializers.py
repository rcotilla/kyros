"""Serializers for tasks app."""

from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'priority',
            'created_by', 'created_by_name', 'assigned_to', 'assigned_to_name',
            'due_date', 'created_at', 'updated_at', 'completed_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'created_by_name', 'assigned_to_name')
