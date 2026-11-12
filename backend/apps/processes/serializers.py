"""Serializers for processes app."""

from rest_framework import serializers
from .models import ProcessType, Process, ProcessStep


class ProcessTypeSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )

    class Meta:
        model = ProcessType
        fields = (
            'id', 'name', 'category', 'category_display',
            'description', 'estimated_days', 'is_active'
        )


class ProcessStepSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name',
        read_only=True,
        default=None
    )

    class Meta:
        model = ProcessStep
        fields = (
            'id', 'name', 'description', 'order', 'status',
            'assigned_to', 'assigned_to_name',
            'due_date', 'completed_at', 'notes'
        )
        read_only_fields = ('id', 'completed_at')


class ProcessListSerializer(serializers.ModelSerializer):
    """Serializer for process list views (compact)."""
    client_name = serializers.CharField(
        source='client.full_name',
        read_only=True
    )
    process_type_name = serializers.CharField(
        source='process_type.name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )

    class Meta:
        model = Process
        fields = (
            'id', 'file_number', 'title', 'client', 'client_name',
            'process_type', 'process_type_name',
            'status', 'status_display', 'priority', 'priority_display',
            'gestor', 'due_date', 'created_at'
        )


class ProcessDetailSerializer(serializers.ModelSerializer):
    """Serializer for process detail views (full info)."""
    client_name = serializers.CharField(
        source='client.full_name',
        read_only=True
    )
    process_type_name = serializers.CharField(
        source='process_type.name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    gestor_name = serializers.CharField(
        source='gestor.get_full_name',
        read_only=True,
        default=None
    )
    operator_name = serializers.CharField(
        source='operator.get_full_name',
        read_only=True,
        default=None
    )
    steps = ProcessStepSerializer(many=True, read_only=True)
    documents_count = serializers.SerializerMethodField()

    class Meta:
        model = Process
        fields = (
            'id', 'file_number', 'title', 'description',
            'process_type', 'process_type_name',
            'client', 'client_name',
            'status', 'status_display', 'priority', 'priority_display',
            'gestor', 'gestor_name', 'operator', 'operator_name',
            'start_date', 'due_date', 'submission_date', 'completion_date',
            'notes', 'external_reference',
            'steps', 'documents_count',
            'created_by', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'file_number', 'created_by', 'created_at', 'updated_at')

    def get_documents_count(self, obj):
        return obj.documents.count()


class ProcessCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating processes."""

    class Meta:
        model = Process
        fields = (
            'title', 'description',
            'process_type', 'client',
            'status', 'priority',
            'gestor', 'operator',
            'start_date', 'due_date', 'submission_date', 'completion_date',
            'notes', 'external_reference',
        )
