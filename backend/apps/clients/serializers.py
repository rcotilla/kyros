"""Serializers for clients app."""

from rest_framework import serializers
from .models import Client


class ClientListSerializer(serializers.ModelSerializer):
    """Serializer for client list views (compact)."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Client
        fields = (
            'id', 'full_name', 'document_type', 'document_number',
            'email', 'phone', 'status', 'assigned_to', 'created_at'
        )


class ClientDetailSerializer(serializers.ModelSerializer):
    """Serializer for client detail views (full info)."""
    full_name = serializers.CharField(read_only=True)
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name',
        read_only=True,
        default=None
    )
    processes_count = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = (
            'id', 'document_type', 'document_number',
            'first_name', 'last_name', 'full_name',
            'nationality', 'birth_date',
            'email', 'phone', 'phone_secondary',
            'address', 'city', 'province', 'postal_code', 'country',
            'notes', 'status',
            'assigned_to', 'assigned_to_name',
            'created_by', 'created_at', 'updated_at',
            'processes_count', 'documents_count',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def get_processes_count(self, obj):
        return obj.processes.count()

    def get_documents_count(self, obj):
        return obj.documents.count()


class ClientCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating clients."""

    class Meta:
        model = Client
        fields = (
            'document_type', 'document_number',
            'first_name', 'last_name',
            'nationality', 'birth_date',
            'email', 'phone', 'phone_secondary',
            'address', 'city', 'province', 'postal_code', 'country',
            'notes', 'status', 'assigned_to',
        )

    def validate_document_number(self, value):
        """Ensure document number is unique (case-insensitive)."""
        instance = self.instance
        qs = Client.objects.filter(document_number__iexact=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'Ya existe un cliente con este número de documento.'
            )
        return value
