"""Serializers for documents app."""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    client_name = serializers.SerializerMethodField()
    process_number = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id', 'title', 'description', 'file', 'doc_type',
            'file_size', 'uploaded_at', 'updated_at', 'is_public',
            'owner', 'owner_name',
            'client', 'client_name',
            'process', 'process_number',
        )
        read_only_fields = ('id', 'file_size', 'uploaded_at', 'updated_at', 'owner_name')

    def get_client_name(self, obj):
        if obj.client:
            return obj.client.full_name
        return None

    def get_process_number(self, obj):
        if obj.process:
            return obj.process.file_number
        return None
